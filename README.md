# Mnyama Collector CLI

**Mnyama Collector** is a Python **Command-Line Interface (CLI)** app for managing wildlife data — animals, species, and habitats — in a structured way.
It combines a local **SQLite database (SQLAlchemy + Alembic)** with **AI-powered image generation** so you can **collect, visualize, and manage virtual creatures**.

---

## Features

* **Creature Management**

  * Add, update, delete, and list creatures
  * Assign species and habitats
  * Track relationships between them

* **Habitat Management**

  * Define habitats (e.g. Savanna, Forest, Ocean)
  * Generate habitat reports

* **Species Management**

  * Store species with scientific names
  * Attach traits and classifications

* **AI Image Generation**

  * Generate creature or habitat images using free APIs:

    * [Pollinations.ai](https://pollinations.ai/) (no signup)
    * [DeepAI](https://deepai.org/) (free tier)
    * [Hugging Face](https://huggingface.co/) (free tier)
  * Store generated image URLs in the database

* **Database Persistence**

  * SQLite backend with **SQLAlchemy ORM**
  * **Alembic** migrations for schema changes

* **Interactive CLI**

  * Menu-based interface
  * Reports & statistics

---

## Project Structure

```
Mnyama-Collector-CLI/
├── .env
├── .gitignore
├── Pipfile
├── Pipfile.lock
├── README.md
└── lib/
    ├── alembic.ini
    ├── cli.py
    ├── creatures.db
    ├── debug.py
    ├── helpers.py
    ├── setup_apis.py
    ├── creature_images/
    ├── migrations/
    │   └── env.py
    └── models/
        ├── __init__.py
        └── models.py

```

---

## Installation & Setup

Follow these steps to set up and run **Mnyama Collector CLI** on your local machine:

### 1. Clone the Repository

```bash
git clone <your-repo-link>
cd Mnyama-Collector-CLI
```

### 2. Set Up Virtual Environment

Make sure you have **Pipenv** installed. Then run:

```bash
pipenv install
pipenv shell
```

### 3. Configure Environment Variables

Create a `.env` file in the **project root** and add your API keys (optional for image generation):

```bash
DEEPAI_API_KEY=your_deepai_key_here
HUGGING_FACE_API_KEY=your_huggingface_key_here
```

### 4. Database Setup (SQLite + Alembic)

Initialize and apply migrations to create/update the database schema:

```bash
cd lib
alembic upgrade head
```

This will create/update `creatures.db` inside the **lib** folder.

### 5. Run the CLI

From the **lib** folder, start the program with:

```bash
python cli.py
```

### 6. (Optional) Debug Mode

To explore and test features interactively, run:

```bash
python debug.py
```

---


## Image API Setup (Optional)

To enable AI image generation:

Run the setup guide:

```bash
python lib/setup_apis.py
```

This will guide you to set up:

* **Pollinations.ai** (works without key)
* **DeepAI** → `export DEEPAI_API_KEY="your-key"`
* **HuggingFace** → `export HUGGING_FACE_API_KEY="your-key"`

---

## Usage

Start the CLI:

```bash
python lib/cli.py
```

Example workflow:

1. Add a new **Species** (Lion)
2. Add a new **Habitat** (Savanna)
3. Add a **Creature** (Simba → species: Lion, habitat: Savanna)
4. Generate an AI image for the creature
5. View **Habitat Report** or **Species Report**

---

## Development Notes

* ORM: SQLAlchemy
* Migrations: Alembic
* DB: SQLite (`creatures.db`)
* APIs: Pollinations, DeepAI, HuggingFace

---

## Roadmap

* [ ] Export reports as PDF/CSV
* [ ] Add search/filter features
* [ ] Offline image caching
* [ ] Unit tests

---

## License

MIT License © 2025 Mohamed Abdul

