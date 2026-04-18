terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud SQL (PostgreSQL + pgvector)
resource "google_sql_database_instance" "postgres" {
  name             = "supaa-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro" # Minimum tier for MVP
  }
  deletion_protection = false
}

resource "google_sql_database" "database" {
  name     = "supaa"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "users" {
  name     = "supaa_admin"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Redis (Memorystore)
resource "google_redis_instance" "cache" {
  name           = "supaa-redis"
  memory_size_gb = 1
  region         = var.region
}

# Cloud Storage
resource "google_storage_bucket" "assets" {
  name     = "supaa-assets-${var.project_id}"
  location = var.region
}

# Cloud Run for API
resource "google_cloud_run_v2_service" "api" {
  name     = "supaa-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "gcr.io/${var.project_id}/supaa-api:latest"
      env {
        name  = "DATABASE_URL"
        value = "postgresql://supaa_admin:${var.db_password}@${google_sql_database_instance.postgres.public_ip_address}/supaa"
      }
      env {
        name  = "REDIS_HOST"
        value = google_redis_instance.cache.host
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "api_public" {
  location = google_cloud_run_v2_service.api.location
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Run for Frontend
resource "google_cloud_run_v2_service" "frontend" {
  name     = "supaa-frontend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "gcr.io/${var.project_id}/supaa-frontend:latest"
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  location = google_cloud_run_v2_service.frontend.location
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
