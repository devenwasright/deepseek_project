import sqlite3
import faiss
import json
import random
import subprocess
import numpy as np
import os
import logging
import asyncio
from sentence_transformers import SentenceTransformer

# Configure logging to log conversation details and errors to a file.
logging.basicConfig(
    filename='agents.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize the SentenceTransformer model with the updated model and dimension.
embedding_model = SentenceTransformer('all-mpnet-base-v2')
embedding_dim = 768  # Updated embedding dimension for all-mpnet-base-v2

# SQLite Database file (created in the current directory)
DB_FILE = "ai_knowledge.db"

class AI_Agent:
    """
    An AI agent that interacts with DeepSeek R1 1.5b, stores knowledge in SQLite,
    and retrieves contextual memory using FAISS vector search.
    """
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.learning_speed = 1.0
        self.self_improvement_cycles = 0
        # Create a FAISS index for embeddings of size embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.knowledge_db = sqlite3.connect(DB_FILE)
        self.create_db_table()

    def create_db_table(self):
        cursor = self.knowledge_db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE,
                content TEXT
            )
        """)
        self.knowledge_db.commit()

    def ask_deepseek(self, prompt):
        """
        Sends a query to DeepSeek R1 1.5b using the Ollama CLI.
        Includes retry logic, uses UTF-8 decoding, and logs details.
        """
        logging.info(f"{self.name} sending prompt: {prompt}")
        try:
            result = subprocess.run(
                ["ollama", "run", "deepseek-r1:1.5b", prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=180  # Increased timeout to 180 seconds
            )
            response = result.stdout.strip()
            logging.info(f"{self.name} (DeepSeek R1 1.5b) returned: {response}")
            return response
        except subprocess.TimeoutExpired:
            logging.error(f"{self.name} (DeepSeek R1 1.5b): Request timed out. Retrying once...")
            try:
                result = subprocess.run(
                    ["ollama", "run", "deepseek-r1:1.5b", prompt],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=180
                )
                response = result.stdout.strip()
                logging.info(f"{self.name} (DeepSeek R1 1.5b) on retry returned: {response}")
                return response
            except subprocess.TimeoutExpired:
                logging.error(f"{self.name} (DeepSeek R1 1.5b): Request timed out again.")
                return "DeepSeek R1 1.5b request timed out."
            except Exception as e:
                logging.error(f"Error on retry connecting to DeepSeek R1 1.5b: {e}")
                return "DeepSeek R1 1.5b is unavailable."
        except Exception as e:
            logging.error(f"Error connecting to DeepSeek R1 1.5b: {e}")
            return "DeepSeek R1 1.5b is unavailable."

    async def ask_deepseek_async(self, prompt):
        """
        Asynchronously wraps the blocking ask_deepseek call using asyncio.to_thread.
        """
        return await asyncio.to_thread(self.ask_deepseek, prompt)

    def learn_topic(self, topic):
        existing = self.retrieve_knowledge(topic)
        if existing:
            logging.info(f"{self.name}: I already know about '{topic}'. Retrieving from memory.")
            return existing
        knowledge = self.ask_deepseek(f"Teach me about {topic} as a {self.role}.")
        self.store_knowledge(topic, knowledge)
        logging.info(f"{self.name}: Learned '{topic}'. Knowledge stored.")
        return knowledge

    def store_knowledge(self, topic, content):
        cursor = self.knowledge_db.cursor()
        cursor.execute("INSERT OR IGNORE INTO knowledge (topic, content) VALUES (?, ?)", (topic, content))
        self.knowledge_db.commit()
        # Generate and add the vector representation using the SentenceTransformer model
        vector = self.generate_vector(content)
        self.index.add(np.array([vector], dtype=np.float32))

    def retrieve_knowledge(self, topic):
        cursor = self.knowledge_db.cursor()
        cursor.execute("SELECT content FROM knowledge WHERE topic=?", (topic,))
        result = cursor.fetchone()
        return result[0] if result else None

    def generate_vector(self, text):
        """
        Uses the SentenceTransformer model to encode the text into a fixed-size vector.
        """
        return embedding_model.encode(text)

    def retrieve_similar_knowledge(self, query):
        query_vector = np.array([self.generate_vector(query)], dtype=np.float32)
        _, indices = self.index.search(query_vector, k=1)
        return indices[0][0]

async def autonomous_conversation(agents, rounds=5):
    """
    Simulates an autonomous conversation between agents asynchronously for a given number of rounds.
    After each round, there is a 30% chance that Creative AI will propose a new topic to switch context.
    """
    message = "Hello, let's begin our autonomous conversation."
    current_agent_index = 0
    for i in range(rounds):
        logging.info(f"--- Round {i+1} ---")
        sender = agents[current_agent_index]
        receiver = agents[(current_agent_index + 1) % len(agents)]
        logging.info(f"{sender.name} sends: {message}")
        reply_prompt = f"As a {receiver.role}, reply to the following message: '{message}'"
        reply = await receiver.ask_deepseek_async(reply_prompt)
        logging.info(f"{receiver.name} replies: {reply}")
        message = reply
        current_agent_index = (current_agent_index + 1) % len(agents)
        await asyncio.sleep(2)
        # Context switching: with a 30% chance, trigger Creative AI to propose a new topic.
        if random.random() < 0.3:
            creative_agent = next((agent for agent in agents if agent.role == "Creative"), None)
            if creative_agent:
                new_topic_prompt = "Propose a new creative conversation topic."
                new_topic = await creative_agent.ask_deepseek_async(new_topic_prompt)
                logging.info(f"{creative_agent.name} proposes new topic: {new_topic}")
                message = new_topic
    return

async def main():
    # Create agents with specialized roles.
    omega_ai = AI_Agent("Omega AI", "Master Coordinator")
    logic_ai = AI_Agent("Logic AI", "Reasoning & Problem-Solving")
    philosopher_ai = AI_Agent("Philosopher AI", "Existential Thinking")
    scientist_ai = AI_Agent("Scientist AI", "Theoretical Research")
    strategist_ai = AI_Agent("Strategist AI", "Future Predictions")
    creative_ai = AI_Agent("Creative AI", "Creative")
    data_analyst_ai = AI_Agent("Data Analyst AI", "Data Analysis & Insights")
    
    # Agents learn topics and store knowledge.
    omega_ai.learn_topic("Singularity Theory")
    scientist_ai.learn_topic("Quantum Computing")
    philosopher_ai.learn_topic("The Nature of Consciousness")
    logic_ai.learn_topic("The Laws of Logic and Reasoning")
    strategist_ai.learn_topic("Predicting Future Technological Trends")
    creative_ai.learn_topic("Creative Idea Generation")
    data_analyst_ai.learn_topic("Data Analysis Methods")
    
    # Retrieve and log stored knowledge.
    logging.info("Retrieving Past Knowledge...")
    logging.info("Quantum Computing: " + (scientist_ai.retrieve_knowledge("Quantum Computing") or "None"))
    logging.info("The Nature of Consciousness: " + (philosopher_ai.retrieve_knowledge("The Nature of Consciousness") or "None"))
    
    # Create the list of agents for conversation.
    agents = [
        omega_ai, logic_ai, philosopher_ai, scientist_ai,
        strategist_ai, creative_ai, data_analyst_ai
    ]
    
    # Start the asynchronous autonomous conversation with the updated context switching.
    await autonomous_conversation(agents, rounds=5)

if __name__ == "__main__":
    asyncio.run(main())
