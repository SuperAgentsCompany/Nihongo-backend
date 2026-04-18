const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

const GEMMA_API_ENDPOINT = "https://gemma4-4b-762452591869.us-central1.run.app/v1/chat/completions";

app.post('/api/chat', async (req, res) => {
  const { prompt } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'Prompt is required' });
  }

  try {
    const response = await fetch(GEMMA_API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: "gemma4-4b",
        messages: [
          { 
            role: "system", 
            content: "You are an expert English-Japanese language teacher. For every response, first think about the pedagogical approach, grammar rules, and cultural context. Wrap your internal monologue in <thought> tags, then provide your final response to the student."
          },
          { role: "user", content: prompt }
        ],
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', errorText);
      return res.status(500).json({ error: 'Failed to communicate with Gemma API' });
    }

    const data = await response.json();
    const message = data.choices[0].message;
    
    let content = message.content || "";
    let reasoning = message.reasoning || "";

    // Extract thoughts from content if present
    if (content.includes('<thought>')) {
      const thoughtMatch = content.match(/<thought>([\s\S]*?)<\/thought>/);
      if (thoughtMatch) {
        reasoning = thoughtMatch[1].trim();
        content = content.replace(/<thought>[\s\S]*?<\/thought>/, '').trim();
      }
    }

    res.json({
      content: content,
      reasoning: reasoning
    });

  } catch (error) {
    console.error('Server Error:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
