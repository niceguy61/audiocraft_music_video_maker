import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import datetime
import numpy as np
import os
import warnings
import logging
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx, ColorClip, CompositeVideoClip
import time
import random
import traceback

# 모든 경고 메시지 숨기기
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.ERROR)

# Lo-Fi / Chill
lofi_settings = {
    "bpm": 75,              # BPM (Beats Per Minute): 음악의 템포를 나타냄. Lo-Fi는 보통 70-85 BPM 사용
    "duration": 300,         # 생성될 음악의 길이(초 단위)
    "temperature": 0.3,     # 생성의 무작위성 정도 (0.0 ~ 1.0)
                           # - 낮을수록 안정적이고 예측 가능한 결과
                           # - 높을수록 창의적이지만 불안정할 수 있음
    "top_k": 40,           # 각 단계에서 고려할 상위 k개의 토큰
                           # - 낮을수록 더 안정적이고 일관된 결과
                           # - 높을수록 더 다양한 결과
    "top_p": 0.7,          # 누적 확률 임계값 (0.0 ~ 1.0)
                           # - 낮을수록 더 보수적인 선택
                           # - 높을수록 더 다양한 선택
    "cfg_coef": 5.0,       # Classifier Free Guidance 계수
                           # - 높을수록 프롬프트를 더 엄격하게 따름
                           # - 낮을수록 더 자유로운 생성
    "genre": "city pop"       # 장르 식별자 (파일명 생성 등에 사용)
}

# Future Bass / Melodic Dubstep
future_bass_settings = {
    "bpm": 150,            # 145-160 BPM 범위
    "duration": 45,        # 드롭을 위해 좀 더 긴 시간
    "temperature": 0.7,    # 창의적인 사운드 디자인을 위해 높게
    "top_k": 250,
    "top_p": 0.9,
    "cfg_coef": 3.0,
    "genre": "future bass"
}

# House / Tech House
house_settings = {
    "bpm": 128,            # 124-130 BPM 범위
    "duration": 40,
    "temperature": 0.65,
    "top_k": 150,
    "top_p": 0.85,
    "cfg_coef": 3.5,
    "genre": "house"
}

# Trap / Hip Hop
trap_settings = {
    "bpm": 140,            # 135-145 BPM 범위
    "duration": 35,
    "temperature": 0.6,
    "top_k": 100,
    "top_p": 0.8,
    "cfg_coef": 3.8,
    "genre": "trap"
}

# Ambient / Atmospheric
ambient_settings = {
    "bpm": 60,             # 60-90 BPM 범위
    "duration": 45,        # 분위기 전개를 위해 좀 더 긴 시간
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 0.7,
    "cfg_coef": 4.5,
    "genre": "ambient"
}

# Drum and Bass
dnb_settings = {
    "bpm": 174,            # 170-180 BPM 범위
    "duration": 35,
    "temperature": 0.75,   # 복잡한 드럼 패턴을 위해 높게
    "top_k": 200,
    "top_p": 0.9,
    "cfg_coef": 3.0,
    "genre": "dnb"
}

# Trance
trance_settings = {
    "bpm": 138,            # 136-142 BPM 범위
    "duration": 45,
    "temperature": 0.6,
    "top_k": 150,
    "top_p": 0.85,
    "cfg_coef": 3.5,
    "genre": "trance"
}

# City Pop 설정
city_pop_settings = {
    "bpm": 104,            # 105-115 BPM 범위가 적합
    "duration": 60,        # 멜로디 전개를 위한 충분한 길이
    "temperature": 0.65,   # 레트로한 느낌과 창의성 균형
    "top_k": 150,
    "top_p": 0.85,
    "cfg_coef": 3.5,
    "genre": "city pop"
}

# Future Funk 설정
future_funk_settings = {
    "bpm": 128,            # 125-130 BPM 범위
    "duration": 40,
    "temperature": 0.7,    # 샘플링과 변형을 위해 약간 높게
    "top_k": 200,
    "top_p": 0.88,
    "cfg_coef": 3.2,
    "genre": "future funk"
}

# City Pop 프롬프트 예시들
city_pop_prompts = [
    # 기본 City Pop
    "japanese city pop with clear song structure and consistent rhythm, "
    "warm electric piano rhodes, funky bass guitar, clean electric guitars, "
    "vintage drum machines maintaining steady beat throughout, "
    "essential structure requirements: "
    "intro 8 bars with distinctive atmospheric opening keeping minimal drums for beat recognition, "
    "clear transition into main sections with multiples of 8 bars, "
    "verses and choruses maintaining steady groove and clear progression, "
    "distinct outro 8 bars with recognizable ending phrase keeping minimal drums, "
    "additional elements: "
    "retro synthesizers, smooth jazz fusion elements, "
    "city night atmosphere, nostalgic 80s japanese production style, "
    "transitions between sections must be clear and well-defined, "
    "maintain consistent tempo and groove for beat matching",
    
    # 현대적 City Pop
    "modern city pop with precise structural arrangement and steady rhythm, "
    "bright brass section, groovy bass lines, clean chorus guitar, "
    "continuous drum pattern for beat tracking, "
    "essential structure requirements: "
    "intro 8 bars with characteristic opening theme and minimal but clear beat, "
    "structured sections in multiples of 8 bars with clear progression, "
    "verses and choruses with distinct melodic themes, "
    "recognizable outro 8 bars with clear ending maintaining minimal rhythm, "
    "additional elements: "
    "vintage synthesizers, analog warmth, summer night vibes, "
    "crystal clear production, sophisticated chord progressions, "
    "all transitions must be well-defined and beat-matched, "
    "ensure consistent tempo throughout for mixing purposes",
    
    # 재즈 영향 City Pop
    "jazz influenced city pop with defined arrangement and steady groove, "
    "smooth saxophone, complex chord progressions, fusion guitar solos, "
    "consistent rhythm section maintaining clear beat, "
    "essential structure requirements: "
    "intro 8 bars with jazz fusion style keeping minimal but present drums, "
    "main sections structured in multiples of 8 bars, "
    "verses and choruses with jazz harmony development, "
    "distinctive outro 8 bars with jazz ending maintaining rhythm, "
    "additional elements: "
    "warm analog synthesizers, elegant strings, "
    "polished production style with clear mix, "
    "ensure all section changes are clearly marked, "
    "maintain steady tempo and groove for beat recognition"
]

# Future Funk 프롬프트 예시들
future_funk_prompts = [
    # 기본 Future Funk
    "energetic future funk with filtered samples, "
    "heavy sidechain compression, punchy drums, "
    "chopped vocal snippets, funky bass groove, "
    "bright synthesizer stabs, vinyl texture, "
    "retro dance vibes with modern production",
    
    # 디스코 영향 Future Funk
    "disco inspired future funk, heavy sampling, "
    "filtered funk loops, strong sidechain pump, "
    "bright synthesizer leads, groovy bass lines, "
    "choppy vocal cuts, energetic rhythm",
    
    # 실험적 Future Funk
    "experimental future funk with glitch elements, "
    "complex sample manipulation, heavy compression, "
    "creative chopping techniques, funky synth layers, "
    "modern electronic production, dance groove"
]

class LocalEDMGenerator:
    def __init__(self):
        # CUDA 설정
        os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"사용중인 디바이스: {self.device}")
        
        try:
            print("모델 로딩 중...")
            # device 파라미터로 직접 지정
            self.model = MusicGen.get_pretrained(
                'facebook/musicgen-melody',
                device=self.device
            )
            
            # 모델 설정
            if hasattr(self.model, 'lm'):
                self.model.lm.cfg.use_cache = True
                
            print("모델 로딩 완료")
            
        except Exception as e:
            print(f"모델 로드 중 오류 발생: {str(e)}")
            raise

    def process_video(self, audio_filename):
        try:
            print("영상 처리 중...")
            # 원본 비디오 로드
            video = VideoFileClip("./youtube_gif_new.mp4")
            
            # 역재생 비디오 생성
            reversed_video = video.fx(vfx.time_mirror)
            
            # 정방향 + 역방향 비디오 연결
            final_video = concatenate_videoclips([video, reversed_video])
            
            # 8초 영상을 음악 길이만큼 반복
            audio = AudioFileClip(f"{audio_filename}.wav")
            num_loops = int(np.ceil(audio.duration / 8))
            
            # 비디오 반복 및 음악 결합
            final_video = concatenate_videoclips([final_video] * num_loops).subclip(0, audio.duration)
            final_video = final_video.set_audio(audio)
            
            # 최종 파일 저장
            output_filename = f"{audio_filename}_with_video.mp4"
            final_video.write_videofile(output_filename, 
                                      codec='libx264', 
                                      audio_codec='aac',
                                      fps=24)
            
            # 리소스 정리
            video.close()
            reversed_video.close()
            final_video.close()
            audio.close()
            
            print(f"\n최종 영상이 생성되었습니다: {output_filename}")
            return True
            
        except Exception as e:
            print(f"영상 처리 중 오류 발생: {str(e)}")
            return False

    def generate_track(self, prompt, settings, progress_callback=None):
        try:
            # progress_callback 처리 방식 수정
            def update_progress(value, desc=""):
                if progress_callback is not None:
                    try:
                        progress_callback(value, desc=desc)
                    except:
                        print(f"Progress update: {value} - {desc}")

            update_progress(0.1, "모델 준비 중...")
            
            # 모델 설정
            self.model.set_generation_params(
                duration=settings['duration'],
                temperature=settings['temperature'],
                top_k=settings['top_k'],
                top_p=settings['top_p'],
                cfg_coef=settings['cfg_coef']
            )
            
            update_progress(0.3, "음악 생성 중...")
            
            # 음악 생성
            wav = self.model.generate([prompt])
            
            update_progress(0.6, "오디오 저장 중...")
            
            # 파일명 생성
            timestamp = int(time.time())
            base_filename = f"{settings['genre']}_{timestamp}"
            audio_path = os.path.join(os.getcwd(), f"{base_filename}.wav")
            video_path = os.path.join(os.getcwd(), f"{base_filename}_with_video.mp4")
            
            # 오디오 저장
            audio_write(
                base_filename, 
                wav[0].cpu(), 
                self.model.sample_rate, 
                strategy="loudness",
                loudness_compressor=True
            )
            
            update_progress(0.8, "비디오 생성 중...")
            
            # 비디오 생성
            success = create_video_with_audio(audio_path, video_path)
            
            if success and os.path.exists(video_path):
                update_progress(1.0, "완료!")
                return video_path
            else:
                print("비디오 생성 실패")
                return None
            
        except Exception as e:
            print(f"트랙 생성 중 오류 발생: {str(e)}")
            traceback.print_exc()
            return None

def create_reversed_clip(clip):
    """비디오 클립을 역재생으로 만드는 함수"""
    return clip.set_make_frame(lambda t: clip.get_frame(clip.duration - t))

def create_video_with_audio(audio_path, output_path):
    try:
        # 오디오 파일 로드
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # YouTube 스타일 애니메이션 로드
        animation_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_gif_new.mp4")
        print(f"애니메이션 파일 경로: {animation_path}")
        
        if not os.path.exists(animation_path):
            print(f"애니메이션 파일을 찾을 수 없습니다: {animation_path}")
            return False
            
        animation = VideoFileClip(animation_path)
        
        # 정방향 + 역방향 한 세트 만들기
        reversed_animation = create_reversed_clip(animation.copy())
        one_set = concatenate_videoclips([animation, reversed_animation])
        
        # 전체 오디오 길이에 맞게 반복
        num_loops = int(np.ceil(duration / one_set.duration))
        final_animation = concatenate_videoclips([one_set] * num_loops)
        
        # 오디오 길이에 맞게 자르기
        final_animation = final_animation.subclip(0, duration)
        
        # 오디오 추가
        final_video = final_animation.set_audio(audio)
        
        print(f"비디오 저장 시작: {output_path}")
        
        # 비디오 저장
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            preset='ultrafast',
            threads=4
        )
        
        # 리소스 정리
        audio.close()
        animation.close()
        reversed_animation.close()
        one_set.close()
        final_animation.close()
        final_video.close()
        
        # 원본 wav 파일 삭제
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        return True
        
    except Exception as e:
        print(f"비디오 생성 중 오류 발생: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        generator = LocalEDMGenerator()
        
        # 더 안정적인 재즈 Lo-Fi 프롬프트
        lofi_jazz_prompt = (
            # 기본 Future Funk
            "japanese city pop with retro synthesizers, "
            "warm electric piano rhodes, funky bass guitar, "
            "smooth jazz fusion elements, clean electric guitars, "
            "vintage drum machines, city night atmosphere, "
            "nostalgic 80s japanese production style, ",
        )
        
        generator.generate_track(
            prompt=city_pop_prompts[1],
            genre_settings=lofi_settings  # 또는 다른 장르 설정
        )
        
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {str(e)}")