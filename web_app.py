import gradio as gr
from main import LocalEDMGenerator
from settings import *  # 설정 파일 임포트
import os
import time
import random

class MusicGenWebApp:
    def __init__(self):
        self.generator = LocalEDMGenerator()
        self.current_settings = None

    def update_settings(self, genre, bpm, temperature, top_k, top_p, cfg_coef):
        """선택된 장르의 설정을 업데이트"""
        settings = get_genre_settings(genre).copy()
        settings.update({
            'bpm': bpm,
            'temperature': temperature,
            'top_k': int(top_k),
            'top_p': top_p,
            'cfg_coef': cfg_coef
        })
        return settings

    def generate_music(self, prompt, genre_select, duration, bpm, temperature, top_k, top_p, cfg_coef, progress=gr.Progress()):
        try:
            # 설정 업데이트
            self.current_settings = self.update_settings(
                genre_select, bpm, temperature, top_k, top_p, cfg_coef
            )
            self.current_settings['duration'] = int(duration)
            
            # 이전 파일들 정리
            self.cleanup_old_files()
            
            # 음악 생성 (직접 파일 경로 받기)
            video_path = self.generator.generate_track(prompt, self.current_settings, progress)
            
            # 파일 존재 여부 확인
            if video_path and os.path.exists(video_path):
                print(f"생성된 비디오 파일: {video_path}")
                return video_path
            else:
                print("비디오 파일 생성 실패")
                return None
                
        except Exception as e:
            print(f"음악 생성 중 오류 발생: {str(e)}")
            return None

    def cleanup_old_files(self):
        """오래된 생성 파일들을 정리"""
        try:
            current_time = time.time()
            for file in os.listdir():
                if file.endswith('.wav') or file.endswith('_with_video.mp4'):
                    file_path = os.path.join(os.getcwd(), file)
                    # 30분 이상 된 파일 삭제
                    if current_time - os.path.getctime(file_path) > 1800:
                        os.remove(file_path)
        except Exception as e:
            print(f"파일 정리 중 오류 발생: {str(e)}")

    def create_ui(self):
        with gr.Blocks(title="AI Music Generator") as app:
            gr.Markdown("# AI Music Generator")
            
            with gr.Row():
                with gr.Column():
                    # 기본 설정
                    genre_select = gr.Dropdown(
                        choices=["City Pop", "Lo-Fi", "Future Bass", "House", 
                                "Trap", "Ambient", "DnB", "Trance"],
                        label="장르 선택",
                        value="City Pop"
                    )
                    
                    duration_slider = gr.Slider(
                        minimum=10,
                        maximum=120,
                        value=30,
                        step=5,
                        label="길이 (초)",
                        info="10초에서 120초 사이 선택"
                    )
                    
                    # 고급 설정 섹션
                    with gr.Accordion("고급 설정", open=False):
                        bpm_slider = gr.Slider(
                            minimum=60,
                            maximum=200,
                            value=120,
                            step=1,
                            label="BPM",
                            info="템포 설정"
                        )
                        
                        temperature_slider = gr.Slider(
                            minimum=0.1,
                            maximum=1.0,
                            value=0.3,
                            step=0.05,
                            label="Temperature",
                            info="높을수록 더 창의적이지만 불안정할 수 있음"
                        )
                        
                        top_k_slider = gr.Slider(
                            minimum=1,
                            maximum=100,
                            value=50,
                            step=1,
                            label="Top K",
                            info="고려할 상위 토큰 수"
                        )
                        
                        top_p_slider = gr.Slider(
                            minimum=0.1,
                            maximum=1.0,
                            value=0.8,
                            step=0.05,
                            label="Top P",
                            info="누적 확률 임계값"
                        )
                        
                        cfg_coef_slider = gr.Slider(
                            minimum=1.0,
                            maximum=10.0,
                            value=5.0,
                            step=0.5,
                            label="CFG Coefficient",
                            info="프롬프트 준수 강도"
                        )
                    
                    prompt_input = gr.Textbox(
                        label="프롬프트 입력",
                        placeholder="음악 생성을 위한 프롬프트를 입력하세요...",
                        lines=5
                    )
                    
                    generate_btn = gr.Button("음악 생성", variant="primary")
                
                with gr.Column():
                    video_output = gr.Video(
                        label="생성된 음악 비디오",
                        autoplay=True
                    )
            
            # 장르 선택시 기본값 업데이트
            def update_default_settings(genre):
                settings = get_genre_settings(genre)
                return [
                    get_default_prompt(genre),  # 프롬프트
                    settings['bpm'],            # BPM
                    settings['temperature'],    # Temperature
                    settings['top_k'],          # Top K
                    settings['top_p'],          # Top P
                    settings['cfg_coef']        # CFG Coefficient
                ]
            
            genre_select.change(
                fn=update_default_settings,
                inputs=[genre_select],
                outputs=[
                    prompt_input,
                    bpm_slider,
                    temperature_slider,
                    top_k_slider,
                    top_p_slider,
                    cfg_coef_slider
                ]
            )
            
            # 생성 버튼 클릭 이벤트
            generate_btn.click(
                fn=self.generate_music,
                inputs=[
                    prompt_input,
                    genre_select,
                    duration_slider,
                    bpm_slider,
                    temperature_slider,
                    top_k_slider,
                    top_p_slider,
                    cfg_coef_slider
                ],
                outputs=[video_output]
            )
            
            # 사용 설명
            with gr.Accordion("사용 방법", open=False):
                gr.Markdown("""
                1. 원하는 장르를 선택하세요
                2. 음악 길이를 설정하세요 (10초-120초)
                3. 필요한 경우 고급 설정을 조정하세요
                4. 프롬프트를 입력하거나 수정하세요
                5. '음악 생성' 버튼을 클릭하세요
                
                고급 설정:
                - BPM: 음악의 템포를 결정합니다
                - Temperature: 높을수록 더 다양한 결과가 나오지만 불안정할 수 있습니다
                - Top K: 각 단계에서 고려할 상위 토큰의 수입니다
                - Top P: 누적 확률 임계값으로, 다양성을 조절합니다
                - CFG Coefficient: 프롬프트 준수 강도를 결정합니다
                """)
        
        return app

if __name__ == "__main__":
    app = MusicGenWebApp()
    webapp = app.create_ui()
    webapp.queue()
    webapp.launch(share=True) 