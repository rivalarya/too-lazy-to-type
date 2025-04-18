import customtkinter as ctk
import pyaudio
import wave
import threading


class AudioRecorder:
    """Handles audio recording functionality"""

    def __init__(self):
        self.recording = False
        self.frames = []

    def start_recording(self):
        """Start recording audio"""
        self.recording = True
        self.frames = []
        thread = threading.Thread(target=self._record_audio)
        thread.start()
        return thread

    def stop_recording(self):
        """Stop recording audio"""
        self.recording = False

    def _record_audio(self):
        """Internal method to record audio"""
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        while self.recording:
            data = stream.read(chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def save_audio(self, filename="recording.wav"):
        """Save recorded audio to file"""
        if not self.frames:
            return None

        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 44100

        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(pyaudio.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        return filename
