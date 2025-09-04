# 🎯 AI Personal Task Prioritizer

A full-stack web application that uses AI to intelligently prioritize your daily tasks based on your main goal. Built with FastAPI backend and vanilla JavaScript frontend.

## ✨ Features

- **AI-Powered Prioritization**: Uses Groq's LLaMA model to analyze and prioritize tasks
- **Interactive Task Management**: Mark tasks as complete with real-time progress tracking
- **Session Persistence**: Save and load your task sessions
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Statistics**: Track your daily progress with visual indicators

## 🏗️ Architecture

```
User Interface (HTML/CSS/JS)
           ↓
    FastAPI Backend (Python)
           ↓
      Groq AI Service
           ↓
    JSON File Storage
```

## 🚀 Tech Stack

**Backend:**
- FastAPI (Python web framework)
- Groq API (AI model integration)
- Pydantic (data validation)
- JSON file storage

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Responsive design with CSS Grid/Flexbox
- Fetch API for backend communication

**Deployment:**
- Vercel (serverless deployment)

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- Groq API key ([Get one here](https://console.groq.com/))

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-task-prioritizer
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

4. **Run the backend server**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

5. **Open the frontend**
   Open `index.html` in your browser or serve it with a local server:
   ```bash
   python -m http.server 3000
   ```

## 🌐 Deployment

### Deploy to Vercel

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Set up environment variables**
   ```bash
   vercel env add GROQ_API_KEY
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Environment Variables

Set these environment variables in your deployment platform:

- `GROQ_API_KEY`: Your Groq API key for AI model access

## 📖 API Documentation

### Endpoints

- `POST /api/prioritize`: Prioritize tasks based on goal
- `GET /api/load`: Load last saved session
- `POST /api/save`: Save current task session
- `PUT /api/tasks/{index}`: Update task completion status

### Example API Usage

```javascript
// Prioritize tasks
const response = await fetch('/api/prioritize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    goal: "Complete project presentation",
    tasks: ["Research topic", "Create slides", "Practice delivery"]
  })
});
```

## 🎨 Features Showcase

- **Smart Prioritization**: AI analyzes task relationships and urgency
- **Visual Priority Indicators**: Color-coded priority levels (High/Medium/Low)
- **Progress Tracking**: Real-time completion statistics
- **Responsive Design**: Optimized for all screen sizes
- **Session Management**: Automatic saving and loading of task sessions

## 🔧 Development

### Project Structure
```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .env.example        # Environment variables template
├── index.html              # Frontend application
├── vercel.json            # Vercel deployment configuration
└── README.md              # Project documentation
```

### Adding New Features

1. **Backend**: Add new endpoints in `backend/main.py`
2. **Frontend**: Update the JavaScript functions in `index.html`
3. **Styling**: Modify the CSS section in `index.html`

## 📝 Resume Highlights

This project demonstrates:

- **Full-Stack Development**: Built complete web application with Python backend and JavaScript frontend
- **AI Integration**: Implemented Groq LLaMA model for intelligent task prioritization with JSON response parsing
- **RESTful API Design**: Created scalable FastAPI backend with proper error handling and data validation using Pydantic

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.