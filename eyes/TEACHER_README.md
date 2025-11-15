# Virtual Teacher 🎓🤖

An interactive AI-powered virtual teacher that **speaks to you** and **illustrates concepts visually** to help you learn anything! Ask questions with your voice and get instant visual and audio explanations.

## Features

- 🎤 **Voice Recognition**: Ask questions by speaking
- 🔊 **Text-to-Speech**: Teacher speaks explanations out loud
- 🎨 **Visual Illustrations**: Automatic diagrams and illustrations
- 📚 **Knowledge Base**: Pre-loaded with math, science, and coding concepts
- 💬 **Interactive**: Real-time conversation with visual feedback
- 📝 **Conversation History**: Tracks your recent questions

## How It Works

1. **Press SPACE** to activate the microphone
2. **Ask your question** (e.g., "What is the Pythagorean theorem?")
3. **Watch & Listen** as the teacher:
   - Shows a visual illustration
   - Explains the concept out loud
   - Provides examples
4. **Learn!** 🎉

## Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements_teacher.txt
```

### Step 2: Install PyAudio (Windows)

PyAudio can be tricky on Windows. Try one of these methods:

**Method 1: Using pip**
```bash
pip install PyAudio
```

**Method 2: If that fails, download the wheel file**
1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Download the appropriate `.whl` file for your Python version
3. Install: `pip install PyAudio‑0.2.11‑cp313‑cp313‑win_amd64.whl`

**Method 3: Alternative (if PyAudio doesn't work)**
You can modify the code to use keyboard input instead of voice input.

## Usage

### Run the Virtual Teacher:

```bash
python virtual_teacher.py
```

### Controls:

- **SPACE**: Activate microphone to ask a question
- **Q**: Quit the application

### Example Questions You Can Ask:

**Mathematics:**
- "What is the Pythagorean theorem?"
- "How does multiplication work?"
- "Explain addition to me"

**Science:**
- "What is photosynthesis?"
- "How does gravity work?"
- "Explain the water cycle"

**Programming:**
- "What are variables?"
- "How do loops work?"
- "What are functions in programming?"

## What You'll See

The interface shows:

### 📺 Main Display
```
┌─────────────────────────────────────────┐
│  VIRTUAL TEACHER          [Status]      │
├─────────────────────────────────────────┤
│  Topic: Pythagorean Theorem             │
├───────────┬─────────────────────────────┤
│           │                             │
│  Visual   │  Detailed Explanation       │
│  Diagram  │  with wrapped text          │
│           │                             │
├───────────┴─────────────────────────────┤
│  Example: Practical example here        │
├─────────────────────────────────────────┤
│  Recent Questions:                      │
│  • What is gravity?                     │
│  • How do variables work?               │
└─────────────────────────────────────────┘
```

### 🎨 Visual Illustrations

The teacher automatically draws:
- **Triangles** for Pythagorean theorem
- **Blocks** for addition
- **Grids** for multiplication
- **Plants** for photosynthesis
- **Planets** for gravity
- **Boxes** for programming variables
- **Loop arrows** for programming loops
- And more!

### 🔊 Audio Feedback

The teacher speaks:
- Complete explanations
- Examples
- Clarifying questions

### 📊 Status Indicators

- 🟢 **Green**: Listening to your question
- 🟠 **Orange**: Speaking/explaining
- ⚪ **Gray**: Ready for next question

## Knowledge Base Topics

### Mathematics
- Pythagorean Theorem
- Addition
- Multiplication

### Science
- Photosynthesis
- Gravity
- Water Cycle

### Programming
- Variables
- Loops
- Functions

## Expanding the Knowledge Base

Want to teach more topics? Edit the `load_knowledge_base()` method in `virtual_teacher.py`:

```python
'your_category': {
    'your_topic': {
        'explanation': 'Detailed explanation here',
        'visual': 'visual_type',  # triangle, blocks, grid, etc.
        'example': 'Practical example here'
    }
}
```

## Adding New Visual Types

Create custom illustrations in the `draw_visual()` method:

```python
elif visual_type == 'your_visual':
    # Your custom drawing code using OpenCV
    cv2.circle(visual_canvas, (200, 150), 50, (255, 100, 100), -1)
    cv2.putText(visual_canvas, 'Text', (100, 200), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
```

## Troubleshooting

### Microphone Not Working
1. Check Windows microphone permissions
2. Run: `python -m speech_recognition` to test
3. Ensure PyAudio is installed correctly
4. Try unplugging/replugging USB microphone

### Speech Recognition Errors
- **"Sorry, I couldn't understand"**: Speak more clearly
- **Connection error**: Check internet connection (Google Speech Recognition requires internet)
- **Timeout**: Speak within 5 seconds of pressing SPACE

### Text-to-Speech Not Working
- pyttsx3 should work offline
- Try adjusting volume: `teacher.tts_engine.setProperty('volume', 1.0)`
- Check system audio settings

### PyAudio Installation Issues
If PyAudio won't install, you can modify the code to use keyboard input instead:

Replace the `listen_for_question()` method:
```python
def listen_for_question(self):
    """Get question from keyboard input"""
    question = input("Ask a question: ")
    return question if question else None
```

## Advanced Features

### Change Voice Speed
Edit line 14 in `virtual_teacher.py`:
```python
self.tts_engine.setProperty('rate', 150)  # 150 = normal, 200 = fast, 100 = slow
```

### Change Voice
```python
voices = self.tts_engine.getProperty('voices')
self.tts_engine.setProperty('voice', voices[1].id)  # Try different indices
```

### Add More Visual Types

Support for:
- Charts and graphs (matplotlib integration)
- Animations (frame-by-frame updates)
- Interactive diagrams
- 3D visualizations

## Integration Ideas

### Connect to AI APIs
Replace the simple knowledge base with:
- **OpenAI GPT**: For unlimited knowledge
- **Claude API**: For detailed explanations
- **Wolfram Alpha**: For math and science
- **Wikipedia API**: For general knowledge

Example integration:
```python
import openai

def find_answer(self, question):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Explain {question} simply"}]
    )
    return response.choices[0].message.content
```

### Save Learning Progress
- Track topics learned
- Generate quizzes
- Save conversation history
- Export notes

### Multi-language Support
- Translate questions/answers
- Support multiple languages for speech
- International phonetic illustrations

## Use Cases

- 📚 **Homework Help**: Get instant explanations
- 👨‍🏫 **Self-Study**: Learn at your own pace
- 🧒 **Kids Education**: Visual and audio learning
- 💼 **Professional Development**: Learn new skills
- ♿ **Accessibility**: Audio explanations for visual impairments
- 🌍 **Language Learning**: Practice pronunciation

## Performance

- **Startup Time**: ~2-3 seconds
- **Response Time**: 1-3 seconds (depending on speech recognition)
- **CPU Usage**: Low (~5-10%)
- **Memory**: ~100-150 MB
- **Internet**: Required for speech recognition only

## Limitations

- Knowledge base is limited (can be expanded)
- Speech recognition requires internet
- English language only (by default)
- Simple illustrations (can be enhanced)
- No handwriting or equation rendering (yet)

## Future Enhancements

Possible improvements:
- 🤖 **AI Integration**: Connect to GPT/Claude for unlimited knowledge
- 📊 **Advanced Graphics**: 3D models, animations, charts
- ✍️ **Equation Rendering**: LaTeX math support
- 📸 **Image Recognition**: Upload diagrams/homework for help
- 🎮 **Gamification**: Points, badges, progress tracking
- 👥 **Multi-user**: Support multiple students
- 📱 **Mobile App**: iOS/Android version
- 🌐 **Web Version**: Browser-based interface
- 💾 **Progress Tracking**: Save learning history
- 🧠 **Adaptive Learning**: Personalized teaching

## Technical Stack

- **Computer Vision**: OpenCV for GUI and illustrations
- **Speech Recognition**: Google Speech Recognition
- **Text-to-Speech**: pyttsx3 (offline, cross-platform)
- **Audio Input**: PyAudio for microphone access
- **Python**: 3.7+

## Credits

Built with:
- OpenCV (https://opencv.org/)
- pyttsx3 (https://github.com/nateshmbhat/pyttsx3)
- SpeechRecognition (https://github.com/Uberi/speech_recognition)
- NumPy (https://numpy.org/)

---

**Happy Learning! 🎓✨**

*"The best teacher is one who suggests rather than dogmatizes, and inspires their students with the wish to teach themselves."* - Edward Bulwer-Lytton

