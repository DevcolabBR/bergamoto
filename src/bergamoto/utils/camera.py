"""
Módulo para captura de fotos usando OpenCV
"""
try:
    import cv2
except ImportError:
    cv2 = None

import io
import threading
from typing import Optional
try:
    from PIL import Image
except ImportError:
    Image = None

import tkinter as tk
from tkinter import messagebox, ttk
try:
    from ttkthemes import ThemedTk
except ImportError:
    ThemedTk = tk.Tk

from .logger import get_logger


class PhotoCapture:
    """Classe para captura de fotos usando OpenCV e Tkinter"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.photo_window_open = False
        self.lock = threading.Lock()
        self.camera = None
        self.root = None
        self.photo_blob = None
        
        # Configurações padrão
        self.CAMERA_DEVICE = 0
        self.THEME = "equilux"
        self.FULLSCREEN = True
        self.AUTO_PHOTO_DELAY = 3000
        self.FRAME_UPDATE_INTERVAL = 10
        self.PHOTO_FORMAT = "PNG"
        
    def capture_photo(self) -> Optional[bytes]:
        """
        Abre janela para capturar foto do funcionário
        
        Returns:
            Bytes da foto em formato PNG ou None se houver erro
        """
        if not cv2:
            self.logger.error("OpenCV não está instalado")
            messagebox.showerror("Erro", "OpenCV não está instalado")
            return None
            
        if not Image:
            self.logger.error("PIL não está instalado")
            messagebox.showerror("Erro", "PIL não está instalado")
            return None
        
        self.photo_blob = None
        
        try:
            with self.lock:
                # Aguardar se outra janela de foto estiver aberta
                while self.photo_window_open:
                    threading.Event().wait(0.1)
                
                self._create_photo_window()
                return self.photo_blob
                
        except Exception as e:
            self.logger.error(f"Erro durante captura de foto: {e}")
            return None
    
    def _create_photo_window(self):
        """Cria a janela de captura de foto"""
        # Inicializar câmera
        self.camera = cv2.VideoCapture(self.CAMERA_DEVICE)
        if not self.camera.isOpened():
            raise Exception("Não foi possível abrir a câmera")
        
        # Criar janela
        try:
            self.root = ThemedTk(theme=self.THEME)
            # Configurar estilo
            style = ttk.Style(self.root)
            style.theme_use(self.THEME)
        except:
            self.root = tk.Tk()
        
        self.root.title("Captura de Foto")
        self.root.attributes("-topmost", True)
        
        if self.FULLSCREEN:
            self.root.attributes("-fullscreen", True)
        
        # Frame principal
        frame = ttk.Frame(self.root, padding="10") if hasattr(ttk, 'Frame') else tk.Frame(self.root)
        frame.pack(expand=True, fill=tk.BOTH)
        
        # Label para preview da câmera
        self.camera_label = ttk.Label(frame) if hasattr(ttk, 'Label') else tk.Label(frame)
        self.camera_label.pack(expand=True)
        
        # Botão para capturar
        capture_button = ttk.Button(
            frame, 
            text="Capturar Foto", 
            command=self._take_photo
        ) if hasattr(ttk, 'Button') else tk.Button(
            frame, 
            text="Capturar Foto", 
            command=self._take_photo
        )
        capture_button.pack(pady=10)
        
        # Bind da tecla Enter
        self.root.bind('<Return>', lambda e: self._take_photo())
        
        # Marcar janela como aberta
        self.photo_window_open = True
        
        # Iniciar preview
        self._start_camera_preview()
        
        # Captura automática após delay
        self.root.after(self.AUTO_PHOTO_DELAY, self._take_photo)
        
        # Iniciar loop da interface
        self.root.mainloop()
        
        # Cleanup
        self._cleanup()
    
    def _start_camera_preview(self):
        """Inicia o preview da câmera"""
        self._update_camera_frame()
    
    def _update_camera_frame(self):
        """Atualiza o frame da câmera no preview"""
        if not self.camera or not self.camera.isOpened():
            return
            
        if not self.root or not self.root.winfo_exists():
            return
        
        try:
            ret, frame = self.camera.read()
            if ret:
                # Converter BGR para RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                
                # Redimensionar se necessário
                display_size = (640, 480)
                pil_image = pil_image.resize(display_size, Image.Resampling.LANCZOS)
                
                # Converter para PhotoImage
                try:
                    from PIL import ImageTk
                    photo = ImageTk.PhotoImage(pil_image)
                    
                    # Atualizar label
                    self.camera_label.configure(image=photo)
                    # Manter referência para evitar garbage collection
                    setattr(self.camera_label, '_photo_ref', photo)
                except ImportError:
                    pass  # Sem preview se ImageTk não estiver disponível
            
            # Agendar próxima atualização
            if self.root and self.root.winfo_exists():
                self.root.after(self.FRAME_UPDATE_INTERVAL, self._update_camera_frame)
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar frame da câmera: {e}")
    
    def _take_photo(self, event=None):
        """Captura a foto atual da câmera"""
        try:
            if not self.camera or not self.camera.isOpened():
                messagebox.showerror("Erro", "Câmera não disponível")
                return
            
            ret, frame = self.camera.read()
            if ret:
                # Converter para PIL Image
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                
                # Converter para bytes PNG
                with io.BytesIO() as output:
                    pil_image.save(output, format=self.PHOTO_FORMAT)
                    self.photo_blob = output.getvalue()
                
                messagebox.showinfo("Sucesso", "Foto capturada com sucesso!")
                self.logger.info("Foto capturada com sucesso")
                
            else:
                messagebox.showerror("Erro", "Falha ao capturar imagem da câmera")
                self.logger.error("Falha ao capturar frame da câmera")
                
        except Exception as e:
            self.logger.error(f"Erro ao capturar foto: {e}")
            messagebox.showerror("Erro", f"Erro ao capturar foto: {str(e)}")
        
        finally:
            # Fechar janela
            if self.root:
                self.root.quit()
    
    def _cleanup(self):
        """Limpa recursos utilizados"""
        if self.camera:
            self.camera.release()
            self.camera = None
            
        if cv2:
            cv2.destroyAllWindows()
        
        if self.root:
            self.root.destroy()
            self.root = None
        
        self.photo_window_open = False
        self.logger.debug("Recursos de captura de foto liberados")