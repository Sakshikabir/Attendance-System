import cv2
import os
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label


# ================= COMMON BUTTON STYLE =================
def styled_button(text, color):
    return Button(
        text=text,
        size_hint=(1, 0.2),
        background_normal='',
        background_color=color,
        font_size=18
    )


# ================= LOGIN SCREEN =================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)

        title = Label(text="📷 Face Attendance System", font_size=28)
        layout.add_widget(title)

        self.name_input = TextInput(
            hint_text="Enter Your Name",
            multiline=False,
            size_hint=(1, 0.2),
            font_size=18
        )
        layout.add_widget(self.name_input)

        btn = styled_button("Login", (0.2, 0.6, 1, 1))
        btn.bind(on_press=self.login)
        layout.add_widget(btn)

        self.status = Label(text="", font_size=16)
        layout.add_widget(self.status)

        self.add_widget(layout)

    def login(self, instance):
        name = self.name_input.text.strip()

        if name == "":
            self.status.text = "❌ Please enter your name"
            return

        self.manager.current = "main"
        self.manager.get_screen("main").set_user(name)


# ================= MAIN SCREEN =================
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.capture = None
        self.user_name = ""
        self.marked = set()

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 🔷 Header
        self.header = Label(text="Welcome", font_size=24, size_hint=(1, 0.1))
        main_layout.add_widget(self.header)

        # 🎥 Camera View
        self.img = Image(size_hint=(1, 0.6))
        main_layout.add_widget(self.img)

        # 🔘 Buttons
        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)

        btn_start = styled_button("Start Camera", (0, 0.7, 0, 1))
        btn_start.bind(on_press=self.start_camera)

        btn_mark = styled_button("Mark", (0, 0.5, 1, 1))
        btn_mark.bind(on_press=self.mark_attendance)

        btn_stop = styled_button("Stop", (1, 0, 0, 1))
        btn_stop.bind(on_press=self.stop_camera)

        btn_layout.add_widget(btn_start)
        btn_layout.add_widget(btn_mark)
        btn_layout.add_widget(btn_stop)

        main_layout.add_widget(btn_layout)

        # 📊 Status Box
        self.status = Label(
            text="Status: Idle",
            size_hint=(1, 0.1),
            font_size=16
        )
        main_layout.add_widget(self.status)

        self.add_widget(main_layout)

    def set_user(self, name):
        self.user_name = name
        self.header.text = f"👋 Welcome, {name}"

    # 🔹 Start Camera
    def start_camera(self, instance):
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)
        self.status.text = "📷 Camera Started"

    # 🔹 Stop Camera
    def stop_camera(self, instance):
        if self.capture:
            self.capture.release()
            self.capture = None
        Clock.unschedule(self.update)
        self.status.text = "🛑 Camera Stopped"

    # 🔹 Camera Feed
    def update(self, dt):
        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]),
                    colorfmt='bgr'
                )
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.img.texture = texture

    # 🔹 Mark Attendance
    def mark_attendance(self, instance):
        if not self.capture:
            self.status.text = "❌ Start camera first"
            return

        ret, frame = self.capture.read()

        if ret:
            os.makedirs("captures", exist_ok=True)

            img_path = f"captures/{self.user_name}_{datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(img_path, frame)

            file = datetime.now().strftime("%Y-%m-%d") + ".csv"

            if self.user_name not in self.marked:
                with open(file, "a") as f:
                    if os.stat(file).st_size == 0:
                        f.write("Name,Date,Time\n")

                    now = datetime.now()
                    f.write(
                        f"{self.user_name},{now.strftime('%Y-%m-%d')},{now.strftime('%H:%M:%S')}\n"
                    )

                self.marked.add(self.user_name)
                self.status.text = "✅ Attendance Marked Successfully"
            else:
                self.status.text = "⚠ Already Marked"


# ================= APP =================
class FaceApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name="main"))
        return sm


if __name__ == "__main__":
    FaceApp().run()