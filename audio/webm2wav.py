from pathlib import Path
from pydub import AudioSegment

def batch_convert(folder_path: str):
    dir_path = Path(folder_path)
    
    for webm_file in dir_path.glob("*.webm"):
        wav_file = webm_file.with_suffix(".wav")
        
        audio = AudioSegment.from_file(webm_file, format="webm")
        audio.export(wav_file, format="wav")
        print(f"変換完了: {webm_file.name} -> {wav_file.name}")

if __name__ == "__main__":
    # 対象のフォルダパスを指定（例: 現在のフォルダ "."）
    batch_convert(".")