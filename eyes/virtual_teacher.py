import cv2
import numpy as np
import pyttsx3
import speech_recognition as sr
import threading
import queue
import time
from datetime import datetime

class VirtualTeacher:
    def __init__(self):
        # Text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speaking speed
        self.tts_engine.setProperty('volume', 0.9)  # Volume
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Visual settings
        self.window_width = 1200
        self.window_height = 800
        self.canvas = None
        
        # State
        self.current_topic = "Ready to teach!"
        self.current_explanation = "Hello! I'm your Virtual Teacher. Ask me anything!"
        self.is_speaking = False
        self.is_listening = False
        self.conversation_history = []
        
        # Queues for thread communication
        self.speech_queue = queue.Queue()
        self.question_queue = queue.Queue()
        
        # Colors
        self.bg_color = (20, 20, 40)
        self.text_color = (255, 255, 255)
        self.accent_color = (100, 200, 255)
        self.teacher_color = (150, 100, 255)
        
        # Running flag
        self.running = False
        
        # Teaching knowledge base (simple examples - can be expanded)
        self.knowledge_base = self.load_knowledge_base()
        
    def load_knowledge_base(self):
        """Load teaching knowledge base with examples and explanations"""
        return {
            'math': {
                'pythagorean theorem': {
                    'explanation': 'The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides. Formula: a squared plus b squared equals c squared.',
                    'visual': 'triangle',
                    'example': 'If a triangle has sides of 3 and 4, the hypotenuse is 5, because 9 plus 16 equals 25.'
                },
                'addition': {
                    'explanation': 'Addition is combining two or more numbers to get a total sum. The plus sign indicates addition.',
                    'visual': 'blocks',
                    'example': '2 plus 3 equals 5. If you have 2 apples and get 3 more, you have 5 apples total.'
                },
                'multiplication': {
                    'explanation': 'Multiplication is repeated addition. When we multiply, we add a number to itself multiple times.',
                    'visual': 'grid',
                    'example': '3 times 4 equals 12. This means 3 plus 3 plus 3 plus 3, or 4 groups of 3.'
                }
            },
            'science': {
                'photosynthesis': {
                    'explanation': 'Photosynthesis is how plants make food using sunlight, water, and carbon dioxide. They produce glucose and oxygen.',
                    'visual': 'plant',
                    'example': 'Plants take in CO2, water, and sunlight, then make sugar for energy and release oxygen we breathe.'
                },
                'gravity': {
                    'explanation': 'Gravity is the force that pulls objects toward each other. Earth\'s gravity keeps us on the ground.',
                    'visual': 'planet',
                    'example': 'When you drop a ball, it falls down because Earth\'s gravity pulls it toward the center.'
                },
                'water cycle': {
                    'explanation': 'The water cycle is how water moves between the ocean, sky, and land through evaporation, condensation, and precipitation.',
                    'visual': 'cycle',
                    'example': 'Water evaporates from oceans, forms clouds, falls as rain, and flows back to the ocean.'
                }
            },
            'coding': {
                'variables': {
                    'explanation': 'Variables are containers that store data in programming. They have a name and hold a value.',
                    'visual': 'box',
                    'example': 'Think of a variable like a labeled box. x equals 5 means the box named x contains the number 5.'
                },
                'loops': {
                    'explanation': 'Loops repeat code multiple times. They help us avoid writing the same code over and over.',
                    'visual': 'loop',
                    'example': 'A for loop can print numbers 1 to 10 without writing 10 separate print statements.'
                },
                'functions': {
                    'explanation': 'Functions are reusable blocks of code that perform specific tasks. They can take inputs and return outputs.',
                    'visual': 'machine',
                    'example': 'A function is like a recipe. You give it ingredients (inputs) and it makes a dish (output).'
                }
            }
        }
    
    def speak(self, text):
        """Convert text to speech"""
        self.is_speaking = True
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            self.is_speaking = False
    
    def listen_for_question(self):
        """Listen for user's question via microphone"""
        self.is_listening = True
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("🔄 Processing...")
            question = self.recognizer.recognize_google(audio)
            print(f"📝 You asked: {question}")
            return question
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return "sorry_unclear"
        except sr.RequestError:
            return "sorry_error"
        except Exception as e:
            print(f"Listen error: {e}")
            return None
        finally:
            self.is_listening = False
    
    def find_answer(self, question):
        """Find answer in knowledge base"""
        question_lower = question.lower()
        
        # Search through knowledge base
        for category, topics in self.knowledge_base.items():
            for topic, content in topics.items():
                if topic in question_lower or any(word in question_lower for word in topic.split()):
                    return {
                        'topic': topic.title(),
                        'category': category.title(),
                        'explanation': content['explanation'],
                        'example': content['example'],
                        'visual': content['visual']
                    }
        
        # If not found, provide general response
        return {
            'topic': 'General Response',
            'category': 'General',
            'explanation': f'That\'s an interesting question about {question}. While I don\'t have specific information on that topic in my knowledge base yet, I can help you learn about math, science, or coding concepts. Try asking about things like the Pythagorean theorem, photosynthesis, or programming variables!',
            'example': 'You can ask me: What is multiplication? How does gravity work? What are variables in programming?',
            'visual': 'question'
        }
    
    def draw_visual(self, visual_type):
        """Draw visual illustration based on type"""
        # Create canvas for illustration
        visual_canvas = np.zeros((300, 400, 3), dtype=np.uint8)
        visual_canvas[:] = (40, 40, 60)
        
        if visual_type == 'triangle':
            # Right triangle for Pythagorean theorem
            pts = np.array([[50, 250], [50, 100], [250, 250]], np.int32)
            cv2.polylines(visual_canvas, [pts], True, (100, 200, 255), 3)
            cv2.putText(visual_canvas, 'a', (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(visual_canvas, 'b', (140, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(visual_canvas, 'c', (140, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
        elif visual_type == 'blocks':
            # Blocks for addition
            for i in range(2):
                cv2.rectangle(visual_canvas, (50 + i*50, 150), (90 + i*50, 190), (255, 100, 100), -1)
            cv2.putText(visual_canvas, '+', (160, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            for i in range(3):
                cv2.rectangle(visual_canvas, (200 + i*50, 150), (240 + i*50, 190), (100, 255, 100), -1)
                
        elif visual_type == 'grid':
            # Grid for multiplication
            for i in range(3):
                for j in range(4):
                    cv2.rectangle(visual_canvas, (50 + j*60, 80 + i*60), 
                                (100 + j*60, 130 + i*60), (255, 200, 100), 2)
            cv2.putText(visual_canvas, '3 x 4 = 12', (100, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                       
        elif visual_type == 'plant':
            # Simple plant for photosynthesis
            cv2.circle(visual_canvas, (200, 80), 40, (255, 255, 100), -1)  # Sun
            cv2.rectangle(visual_canvas, (180, 150), (220, 250), (139, 69, 19), -1)  # Stem
            cv2.circle(visual_canvas, (150, 120), 30, (100, 255, 100), -1)  # Leaf
            cv2.circle(visual_canvas, (250, 120), 30, (100, 255, 100), -1)  # Leaf
            cv2.arrowedLine(visual_canvas, (200, 50), (200, 100), (255, 255, 0), 2)  # Sunlight
            
        elif visual_type == 'planet':
            # Earth for gravity
            cv2.circle(visual_canvas, (200, 150), 80, (100, 150, 255), -1)
            cv2.circle(visual_canvas, (200, 150), 80, (255, 255, 255), 2)
            cv2.circle(visual_canvas, (200, 60), 10, (255, 100, 100), -1)  # Object
            cv2.arrowedLine(visual_canvas, (200, 70), (200, 130), (255, 255, 255), 2)  # Arrow down
            
        elif visual_type == 'box':
            # Box for variables
            cv2.rectangle(visual_canvas, (120, 100), (280, 200), (150, 100, 255), 3)
            cv2.putText(visual_canvas, 'x = 5', (150, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
                       
        elif visual_type == 'loop':
            # Loop arrows
            cv2.ellipse(visual_canvas, (200, 150), (80, 80), 0, 0, 270, (100, 255, 200), 3)
            cv2.arrowedLine(visual_canvas, (200, 70), (180, 70), (100, 255, 200), 3)
            cv2.putText(visual_canvas, 'Repeat', (160, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                       
        elif visual_type == 'question':
            # Question mark
            cv2.putText(visual_canvas, '?', (160, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 4, (150, 150, 255), 6)
        
        return visual_canvas
    
    def draw_interface(self):
        """Draw the main teaching interface"""
        # Create main canvas
        canvas = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)
        canvas[:] = self.bg_color
        
        # Header
        cv2.rectangle(canvas, (0, 0), (self.window_width, 80), (40, 40, 80), -1)
        cv2.putText(canvas, "VIRTUAL TEACHER", (30, 50), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, self.accent_color, 2)
        
        # Status indicators
        status_y = 40
        if self.is_listening:
            cv2.circle(canvas, (self.window_width - 150, status_y), 15, (100, 255, 100), -1)
            cv2.putText(canvas, "Listening...", (self.window_width - 130, status_y + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        elif self.is_speaking:
            cv2.circle(canvas, (self.window_width - 150, status_y), 15, (255, 200, 100), -1)
            cv2.putText(canvas, "Speaking...", (self.window_width - 130, status_y + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            cv2.circle(canvas, (self.window_width - 150, status_y), 15, (150, 150, 150), -1)
            cv2.putText(canvas, "Ready", (self.window_width - 130, status_y + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Current topic
        cv2.putText(canvas, f"Topic: {self.current_topic}", (30, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, self.teacher_color, 2)
        
        # Visual illustration area
        if hasattr(self, 'current_visual'):
            visual = self.draw_visual(self.current_visual)
            canvas[150:450, 50:450] = visual
        
        # Explanation area
        explanation_y = 150
        explanation_x = 480
        max_width = self.window_width - explanation_x - 30
        
        # Draw explanation box
        cv2.rectangle(canvas, (explanation_x - 10, explanation_y - 10), 
                     (self.window_width - 20, 600), (40, 40, 60), -1)
        cv2.rectangle(canvas, (explanation_x - 10, explanation_y - 10), 
                     (self.window_width - 20, 600), self.accent_color, 2)
        
        # Wrap and display explanation text
        if self.current_explanation:
            self.draw_wrapped_text(canvas, self.current_explanation, 
                                 explanation_x, explanation_y, max_width, 30)
        
        # Example area
        if hasattr(self, 'current_example'):
            cv2.putText(canvas, "Example:", (50, 500), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 100), 2)
            self.draw_wrapped_text(canvas, self.current_example, 
                                 50, 530, self.window_width - 100, 25)
        
        # Conversation history (last 3)
        history_y = 650
        cv2.line(canvas, (30, history_y - 20), (self.window_width - 30, history_y - 20), 
                (100, 100, 100), 1)
        cv2.putText(canvas, "Recent Questions:", (30, history_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
        
        for i, item in enumerate(self.conversation_history[-3:]):
            y_pos = history_y + 30 + i * 30
            cv2.putText(canvas, f"• {item}", (50, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Instructions
        cv2.putText(canvas, "Press SPACE to ask a question | Press 'q' to quit", 
                   (30, self.window_height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        
        return canvas
    
    def draw_wrapped_text(self, canvas, text, x, y, max_width, line_height):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            size = cv2.getTextSize(test_line, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            if size[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        for i, line in enumerate(lines):
            cv2.putText(canvas, line, (x, y + i * line_height), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1)
    
    def handle_question(self, question):
        """Process and answer a question"""
        if question and question not in ["sorry_unclear", "sorry_error"]:
            # Add to history
            self.conversation_history.append(question[:50])
            
            # Find answer
            answer = self.find_answer(question)
            
            # Update display
            self.current_topic = answer['topic']
            self.current_explanation = answer['explanation']
            self.current_example = answer['example']
            self.current_visual = answer['visual']
            
            # Speak the answer
            speech_text = f"Let me explain {answer['topic']}. {answer['explanation']} For example, {answer['example']}"
            threading.Thread(target=self.speak, args=(speech_text,), daemon=True).start()
            
        elif question == "sorry_unclear":
            self.current_explanation = "Sorry, I couldn't understand that. Please try speaking more clearly."
            threading.Thread(target=self.speak, 
                           args=("Sorry, I couldn't understand that. Please try again.",), 
                           daemon=True).start()
        elif question == "sorry_error":
            self.current_explanation = "Sorry, there was an error with speech recognition. Please check your internet connection."
            threading.Thread(target=self.speak, 
                           args=("Sorry, there was a connection error.",), 
                           daemon=True).start()
    
    def run(self):
        """Main loop"""
        print("=" * 60)
        print("VIRTUAL TEACHER STARTING...")
        print("=" * 60)
        print("Initializing microphone...")
        
        # Warm up microphone
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("Ready to teach!")
        print("=" * 60)
        
        # Initial greeting
        greeting = "Hello! I'm your Virtual Teacher. Press space and ask me anything about math, science, or coding!"
        threading.Thread(target=self.speak, args=(greeting,), daemon=True).start()
        
        self.running = True
        
        while self.running:
            # Draw interface
            canvas = self.draw_interface()
            cv2.imshow('Virtual Teacher', canvas)
            
            # Handle keyboard
            key = cv2.waitKey(100) & 0xFF
            
            if key == ord('q'):
                self.running = False
                break
            elif key == ord(' ') and not self.is_listening and not self.is_speaking:
                # Listen for question
                question = self.listen_for_question()
                if question:
                    self.handle_question(question)
        
        cv2.destroyAllWindows()
        print("\nGoodbye! Happy learning!")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                 VIRTUAL TEACHER                           ║
    ║                                                           ║
    ║  An interactive AI teacher that speaks and illustrates!  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    teacher = VirtualTeacher()
    
    try:
        teacher.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

