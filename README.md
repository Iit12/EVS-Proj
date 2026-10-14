# EVS-Proj

## 🌍 EcoAwareness AI — Environmental Awareness Poster Generator

An AI-powered application that generates impactful environmental awareness posters with headlines, messages, practical tips, and slogans, fully rendered into downloadable high-resolution posters.

### 🌟 Features
- **AI-Powered Content Generation**: Powered by **Ollama (`llama3.2`)**, with cloud API and offline fallbacks.
- **Multilingual Support**: Generate content in English, Hindi, and Kannada.
- **Automatic Poster Rendering**: Uses Pillow to design posters with custom typography and palettes.
- **Interactive UI**: Built with Streamlit for quick topic selection, live generation, and instant PNG downloads.

### 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   cd "evs mini"
   pip install -r requirements.txt
   ```

2. **Run Ollama**:
   ```bash
   ollama run llama3.2
   ```

3. **Launch the Streamlit App**:
   ```bash
   streamlit run app.py
   ```
