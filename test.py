import vlc
import time
from gtts import gTTS
import subprocess


def speak_sentence(text: str, language: str) -> None:
    tts = gTTS(text=text, lang=language)
    tts.save("output.mp3")

    # Play the saved MP3 file
    player: vlc.MediaPlayer = vlc.MediaPlayer("output.mp3")
    player.play()
    time.sleep(1)  # Wait for VLC to start playing
    while player.is_playing():
        time.sleep(1)  # Wait for the audio to finish


if __name__ == "__main__":
    text = """
    国土交通省は5月ごろから、客が多い時間と少ない時間でタクシーの料金を変えることができる制度を始めます。国に申し込みをした会社は、客がスマートフォンのアプリを使ってタクシーを呼ぶ場合、料金を変えることができます。例えば、客が少ない昼は安くします。しかし、雨の日や金曜日の夜など、客が多くなりそうなときは、料金を上げます。アプリを使わない場合より、50%まで安くすることや高くすることができます。国は、３か月に１度タクシー会社をチェックして、料金が高くなりすぎないようにします。
    """

    text = text.replace("\n", " ")
    command = f'python3 translate.py -t {text} SV'

    result = subprocess.run(command, shell=True, text=True,
                            capture_output=True, encoding="utf-8")

    if result.returncode == 0:
        translated_text = result.stdout.strip()
        print(translated_text)
        speak_sentence(translated_text, language="sv")
    else:
        print("Translation failed")
        print("Error:", result.stderr)
