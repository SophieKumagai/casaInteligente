import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
import threading
import random
import time

class SmartHome:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulação de Casa Inteligente com Planta Baixa")

        # Variáveis do sensor
        self.temperature = tk.DoubleVar(value=25.0)
        self.humidity = tk.DoubleVar(value=50.0)
        self.motion = tk.BooleanVar(value=False)

        # Variáveis do atuador
        self.light_on_sala_estar = tk.BooleanVar(value=False)
        self.light_on_cozinha = tk.BooleanVar(value=False)
        self.light_on_quarto = tk.BooleanVar(value=False)
        self.light_on_banheiro = tk.BooleanVar(value=False)

        self.ac_on_sala_estar = tk.BooleanVar(value=False)
        self.ac_on_quarto = tk.BooleanVar(value=False)

        # Modo de operação
        self.mode = tk.StringVar(value="Manual")

        # Carregar ícones (substitua pelos caminhos reais das imagens)
        try:
            self.temp_icon = PhotoImage(file="temperature1.png")
            self.humidity_icon = PhotoImage(file="humidity1.png")
            self.motion_icon = PhotoImage(file="motion1.png")
            self.light_icon = PhotoImage(file="light1.png")
            self.ac_icon = PhotoImage(file="ac1.png")
        except tk.TclError:
            print("Erro ao carregar imagens. Usando rótulos de texto em vez disso.")
            self.temp_icon = None
            self.humidity_icon = None
            self.motion_icon = None
            self.light_icon = None
            self.ac_icon = None

        self.create_widgets()

        # Variável de modo de rastreamento para atualizar o estado dos controles
        self.mode.trace_add("write", self.on_mode_change)

        self.running = True

        # Thread para atualizações de sensores (temperatura e umidade apenas)
        self.sensor_thread = threading.Thread(target=self.update_sensors)
        self.sensor_thread.daemon = True
        self.sensor_thread.start()

        # Thread para controle automático
        self.control_thread = threading.Thread(target=self.automatic_control)
        self.control_thread.daemon = True
        self.control_thread.start()

    def create_widgets(self):
        # Quadro principal
        main_frame = ttk.Frame(self.root, padding=16)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Quadro esquerdo: Controles de Sensores e Atuadores
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        control_frame.columnconfigure(0, weight=1)

        # QUADRO DE SENSORES -----------------------------------
        sensor_frame = ttk.LabelFrame(control_frame, text="Sensores", padding=16)
        sensor_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        sensor_frame.columnconfigure(1, weight=1)

        # Temperatura
        ttk.Label(sensor_frame, text="Temperatura:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=5, pady=6)
        if self.temp_icon:
            temp_label = ttk.Label(sensor_frame, image=self.temp_icon)
            temp_label.image = self.temp_icon
            temp_label.grid(row=0, column=2, sticky="e", padx=5, pady=6)
        ttk.Label(sensor_frame, textvariable=self.temperature, font=('Segoe UI', 10)).grid(row=0, column=1, sticky="e", padx=5, pady=6)
        ttk.Label(sensor_frame, text="°C", font=('Segoe UI', 10)).grid(row=0, column=3, sticky="w", padx=5, pady=6)

        # Umidade
        ttk.Label(sensor_frame, text="Umidade:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky="w", padx=5, pady=6)
        if self.humidity_icon:
            humidity_label = ttk.Label(sensor_frame, image=self.humidity_icon)
            humidity_label.image = self.humidity_icon
            humidity_label.grid(row=1, column=2, sticky="e", padx=5, pady=6)
        ttk.Label(sensor_frame, textvariable=self.humidity, font=('Segoe UI', 10)).grid(row=1, column=1, sticky="e", padx=5, pady=6)
        ttk.Label(sensor_frame, text="%", font=('Segoe UI', 10)).grid(row=1, column=3, sticky="w", padx=5, pady=6)

        # Movimento
        self.motion_label = ttk.Label(sensor_frame, text="Movimento:", font=('Segoe UI', 10, 'bold'))
        self.motion_label.grid(row=2, column=0, sticky="w", padx=5, pady=6)

        if self.motion_icon:
            self.motion_icon_label = ttk.Label(sensor_frame, image=self.motion_icon)
            self.motion_icon_label.image = self.motion_icon
            self.motion_icon_label.grid(row=2, column=2, sticky="e", padx=5, pady=6)
            self.motion_icon_label.bind("<Enter>", self.on_motion_hover_enter)
            self.motion_icon_label.bind("<Leave>", self.on_motion_hover_leave)
        else:
            self.motion_text_label = ttk.Label(sensor_frame, textvariable=self.motion, font=('Segoe UI', 10))
            self.motion_text_label.grid(row=2, column=1, sticky="e", padx=5, pady=6)
            self.motion_text_label.bind("<Enter>", self.on_motion_hover_enter)
            self.motion_text_label.bind("<Leave>", self.on_motion_hover_leave)

        # Rótulo de última atualização
        self.last_updated_label = ttk.Label(sensor_frame, text="Última atualização: N/A", font=('Segoe UI', 8))
        self.last_updated_label.grid(row=4, column=0, columnspan=4, sticky="w", padx=5, pady=8)

        # QUADRO DE ATUADORES -----------------------------------
        actuator_frame = ttk.LabelFrame(control_frame, text="Atuadores", padding=16)
        actuator_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        actuator_frame.columnconfigure(1, weight=1)

        # Luz da Sala de Estar
        ttk.Label(actuator_frame, text="Luz da Sala de Estar:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=5, pady=8)
        if self.light_icon:
            light_label = ttk.Label(actuator_frame, image=self.light_icon)
            light_label.image = self.light_icon
            light_label.grid(row=0, column=2, sticky="e", padx=5, pady=8)
        self.light_sala_estar_check = ttk.Checkbutton(actuator_frame, variable=self.light_on_sala_estar, command=self.update_icons_for_all_rooms)
        self.light_sala_estar_check.grid(row=0, column=1, sticky="e", padx=5, pady=8)

        # Luz da Cozinha
        ttk.Label(actuator_frame, text="Luz da Cozinha:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky="w", padx=5, pady=8)
        if self.light_icon:
            light_label = ttk.Label(actuator_frame, image=self.light_icon)
            light_label.image = self.light_icon
            light_label.grid(row=1, column=2, sticky="e", padx=5, pady=8)
        self.light_cozinha_check = ttk.Checkbutton(actuator_frame, variable=self.light_on_cozinha, command=self.update_icons_for_all_rooms)
        self.light_cozinha_check.grid(row=1, column=1, sticky="e", padx=5, pady=8)

        # Luz do Quarto
        ttk.Label(actuator_frame, text="Luz do Quarto:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky="w", padx=5, pady=8)
        if self.light_icon:
            light_label = ttk.Label(actuator_frame, image=self.light_icon)
            light_label.image = self.light_icon
            light_label.grid(row=2, column=2, sticky="e", padx=5, pady=8)
        self.light_quarto_check = ttk.Checkbutton(actuator_frame, variable=self.light_on_quarto, command=self.update_icons_for_all_rooms)
        self.light_quarto_check.grid(row=2, column=1, sticky="e", padx=5, pady=8)

        # Luz do Banheiro
        ttk.Label(actuator_frame, text="Luz do Banheiro:", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky="w", padx=5, pady=8)
        if self.light_icon:
            light_label = ttk.Label(actuator_frame, image=self.light_icon)
            light_label.image = self.light_icon
            light_label.grid(row=3, column=2, sticky="e", padx=5, pady=8)
        self.light_banheiro_check = ttk.Checkbutton(actuator_frame, variable=self.light_on_banheiro, command=self.update_icons_for_all_rooms)
        self.light_banheiro_check.grid(row=3, column=1, sticky="e", padx=5, pady=8)

        # Ar Condicionado Sala de Estar
        ttk.Label(actuator_frame, text="Ar Condicionado da Sala de Estar:", font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky="w", padx=5, pady=8)
        if self.ac_icon:
            ac_label = ttk.Label(actuator_frame, image=self.ac_icon)
            ac_label.image = self.ac_icon
            ac_label.grid(row=4, column=2, sticky="e", padx=5, pady=8)
        self.ac_sala_estar_check = ttk.Checkbutton(actuator_frame, variable=self.ac_on_sala_estar, command=self.update_icons_for_all_rooms)
        self.ac_sala_estar_check.grid(row=4, column=1, sticky="e", padx=5, pady=8)

        # Ar Condicionado Quarto
        ttk.Label(actuator_frame, text="Ar Condicionado do Quarto:", font=('Segoe UI', 10, 'bold')).grid(row=5, column=0, sticky="w", padx=5, pady=8)
        if self.ac_icon:
            ac_label = ttk.Label(actuator_frame, image=self.ac_icon)
            ac_label.image = self.ac_icon
            ac_label.grid(row=5, column=2, sticky="e", padx=5, pady=8)
        self.ac_quarto_check = ttk.Checkbutton(actuator_frame, variable=self.ac_on_quarto, command=self.update_icons_for_all_rooms)
        self.ac_quarto_check.grid(row=5, column=1, sticky="e", padx=5, pady=8)

        # Botão de redefinir atuadores
        self.reset_button = ttk.Button(actuator_frame, text="Redefinir Atuadores", command=self.reset_actuators)
        self.reset_button.grid(row=6, column=0, columnspan=3, sticky="we", pady=(20, 0))

        # QUADRO DE MODO -----------------------------------
        mode_frame = ttk.LabelFrame(control_frame, text="Modo de Operação", padding=16)
        mode_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        mode_frame.columnconfigure((1, 2), weight=1)

        ttk.Radiobutton(mode_frame, text="Manual", variable=self.mode, value="Manual").grid(row=0, column=1, sticky="w", padx=10)
        ttk.Radiobutton(mode_frame, text="Automático", variable=self.mode, value="Automático").grid(row=0, column=2, sticky="w", padx=10)

        # Quadro direito: Desenho da planta da casa
        plan_frame = ttk.LabelFrame(main_frame, text="Layout da Casa", padding=16)
        plan_frame.grid(row=0, column=1, sticky=(tk.N, tk.E, tk.S), padx=(20, 0))
        plan_frame.rowconfigure(0, weight=1)
        plan_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(plan_frame, width=400, height=500, bg="#f0f0f0", highlightthickness=1, highlightbackground="#888")
        self.canvas.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.draw_floor_plan()

        # Chamada inicial para definir os estados dos widgets com base no modo
        self.on_mode_change()

    def draw_floor_plan(self):
        c = self.canvas
        c.delete("all")

        wall_color = "#666"

        # Desenhar cômodos e associar tags para monitorar enter/leave do mouse
        # Sala de Estar
        c.create_rectangle(30, 30, 200, 250, fill="#d1e7dd", outline=wall_color, width=2, tags=("room", "livingroom"))
        c.create_text(115, 140, text="Sala de Estar", font=("Segoe UI", 14, "bold"), fill="#0f5132")

        # Cozinha
        c.create_rectangle(210, 30, 370, 150, fill="#fff3cd", outline=wall_color, width=2, tags=("room", "kitchen"))
        c.create_text(290, 90, text="Cozinha", font=("Segoe UI", 14, "bold"), fill="#664d03")

        # Quarto
        c.create_rectangle(210, 160, 370, 320, fill="#cfe2ff", outline=wall_color, width=2, tags=("room", "bedroom"))
        c.create_text(290, 240, text="Quarto", font=("Segoe UI", 14, "bold"), fill="#084298")

        # Banheiro
        c.create_rectangle(30, 260, 200, 480, fill="#f8d7da", outline=wall_color, width=2, tags=("room", "bathroom"))
        c.create_text(115, 370, text="Banheiro", font=("Segoe UI", 14, "bold"), fill="#842029")

        # Desenhar portas e janelas
        c.create_line(115, 250, 115, 260, fill=wall_color, width=4)
        c.create_rectangle(70, 25, 140, 18, fill="#0d6efd", outline="#0d6efd")
        c.create_rectangle(250, 25, 320, 18, fill="#0d6efd", outline="#0d6efd")
        c.create_rectangle(350, 180, 357, 230, fill="#0d6efd", outline="#0d6efd")

        # Móveis
        c.create_rectangle(40, 80, 170, 130, fill="#6c757d", outline="#495057", width=2)
        c.create_text(105, 105, text="Sofá", fill="white", font=("Segoe UI", 10, "bold"))
        c.create_oval(80, 160, 150, 210, fill="#adb5bd", outline="#6c757d")
        c.create_rectangle(230, 50, 290, 120, fill="#343a40", outline="#212529", width=2)
        c.create_text(260, 85, text="Fogão", fill="white", font=("Segoe UI", 10, "bold"))
        c.create_rectangle(230, 180, 350, 300, fill="#0d6efd", outline="#084298", width=3)
        c.create_text(290, 240, text="Cama", fill="white", font=("Segoe UI", 12, "bold"))
        c.create_oval(50, 300, 120, 370, fill="#6f42c1", outline="#4b229b", width=2)
        c.create_text(85, 335, text="Pia", fill="white", font=("Segoe UI", 10, "bold"))

        # Ícones sensores fixos de temperatura e umidade
        if self.temp_icon:
            self.canvas.create_image(280, 140, image=self.temp_icon)
        if self.humidity_icon:
            self.canvas.create_image(90, 400, image=self.humidity_icon)

        # Associa eventos de mouse enter e leave para cada cômodo para detectar movimento
        for room_tag in ("livingroom", "kitchen", "bedroom", "bathroom"):
            c.tag_bind(room_tag, "<Enter>", self.on_motion_hover_enter_canvas)
            c.tag_bind(room_tag, "<Leave>", self.on_motion_hover_leave_canvas)

        # Dicionários para armazenar IDs dos ícones de luz e AC em cada cômodo
        self.room_light_icons = {}
        self.room_ac_icons = {}

        # Coordenadas para os pequenos ícones de luz e AC dentro de cada cômodo (aproximadas)
        coords = {
            "livingroom": (80, 60),
            "kitchen": (270, 60),
            "bedroom": (290, 200),
            "bathroom": (100, 300),
        }

        # Desenhar ícones pequenos para luz e ar condicionado em cada cômodo
        for room, (x, y) in coords.items():
            # Luz: círculo amarelo/claro para ligado, cinza para desligado
            light_color = "#6c757d"  # cor inicial desligada
            ac_color = "#6c757d"  # cor inicial desligada
            if room == "livingroom":
                light_color = "#ffc107" if self.light_on_sala_estar.get() else "#6c757d"
                ac_color = "#0dcaf0" if self.ac_on_sala_estar.get() else "#6c757d"
                light_id = c.create_oval(x-10, y-10, x+10, y+10, fill=light_color, outline="")
                ac_id = c.create_rectangle(x-10, y+15, x+10, y+35, fill=ac_color, outline="")
                self.room_light_icons[room] = light_id
                self.room_ac_icons[room] = ac_id
            elif room == "kitchen":
                light_color = "#ffc107" if self.light_on_cozinha.get() else "#6c757d"
                light_id = c.create_oval(x-10, y-10, x+10, y+10, fill=light_color, outline="")
                self.room_light_icons[room] = light_id
                # Sem ícone de AC para cozinha
            elif room == "bedroom":
                light_color = "#ffc107" if self.light_on_quarto.get() else "#6c757d"
                ac_color = "#0dcaf0" if self.ac_on_quarto.get() else "#6c757d"
                light_id = c.create_oval(x-10, y-10, x+10, y+10, fill=light_color, outline="")
                ac_id = c.create_rectangle(x-10, y+15, x+10, y+35, fill=ac_color, outline="")
                self.room_light_icons[room] = light_id
                self.room_ac_icons[room] = ac_id
            elif room == "bathroom":
                light_color = "#ffc107" if self.light_on_banheiro.get() else "#6c757d"
                light_id = c.create_oval(x-10, y-10, x+10, y+10, fill=light_color, outline="")
                self.room_light_icons[room] = light_id
                # Sem ícone de AC para banheiro

        # Atualizar ícones para refletir corretamente os estados atuais
        self.update_icons_for_all_rooms()

    # Eventos de hover do mouse nos cômodos para sensor de movimento
    def on_motion_hover_enter_canvas(self, event=None):
        tags = self.canvas.gettags("current")
        if not tags:
            return
        if self.mode.get() != "Automático":
            return  # só responde no modo automático
        if "livingroom" in tags:
            self.light_on_sala_estar.set(True)
            if self.temperature.get() > 28:
                self.ac_on_sala_estar.set(True)
        elif "kitchen" in tags:
            self.light_on_cozinha.set(True)
        elif "bedroom" in tags:
            self.light_on_quarto.set(True)
            if self.temperature.get() > 28:
                self.ac_on_quarto.set(True)
        elif "bathroom" in tags:
            self.light_on_banheiro.set(True)
        self.motion.set(True)
        self.update_icons_for_all_rooms()

    def on_motion_hover_leave_canvas(self, event=None):
        tags = self.canvas.gettags("current")
        if not tags:
            return
        if self.mode.get() != "Automático":
            return
        if "livingroom" in tags:
            self.light_on_sala_estar.set(False)
            self.ac_on_sala_estar.set(False)
        elif "kitchen" in tags:
            self.light_on_cozinha.set(False)
        elif "bedroom" in tags:
            self.light_on_quarto.set(False)
            self.ac_on_quarto.set(False)
        elif "bathroom" in tags:
            self.light_on_banheiro.set(False)
        self.motion.set(False)
        self.update_icons_for_all_rooms()

    # Atualizar os pequenos ícones de luz e AC em todos os cômodos
    def update_icons_for_all_rooms(self):
        c = self.canvas
        light_color_on = "#ffc107"
        light_color_off = "#6c757d"
        ac_color_on = "#0dcaf0"
        ac_color_off = "#6c757d"

        # Atualizar Sala de Estar
        light_id = self.room_light_icons.get("livingroom")
        ac_id = self.room_ac_icons.get("livingroom")
        if light_id:
            new_light_color = light_color_on if self.light_on_sala_estar.get() else light_color_off
            c.itemconfig(light_id, fill=new_light_color)
        if ac_id:
            new_ac_color = ac_color_on if self.ac_on_sala_estar.get() else ac_color_off
            c.itemconfig(ac_id, fill=new_ac_color)

        # Atualizar Cozinha
        light_id = self.room_light_icons.get("kitchen")
        if light_id:
            new_light_color = light_color_on if self.light_on_cozinha.get() else light_color_off
            c.itemconfig(light_id, fill=new_light_color)

        # Atualizar Quarto
        light_id = self.room_light_icons.get("bedroom")
        ac_id = self.room_ac_icons.get("bedroom")
        if light_id:
            new_light_color = light_color_on if self.light_on_quarto.get() else light_color_off
            c.itemconfig(light_id, fill=new_light_color)
        if ac_id:
            new_ac_color = ac_color_on if self.ac_on_quarto.get() else ac_color_off
            c.itemconfig(ac_id, fill=new_ac_color)

        # Atualizar Banheiro
        light_id = self.room_light_icons.get("bathroom")
        if light_id:
            new_light_color = light_color_on if self.light_on_banheiro.get() else light_color_off
            c.itemconfig(light_id, fill=new_light_color)

    # Evento de hover do mouse no ícone/rótulo de movimento no quadro de controles - também atualiza o estado de movimento + luz
    def on_motion_hover_enter(self, event=None):
        self.motion.set(True)
        if self.mode.get() == "Automático":
            self.light_on_sala_estar.set(True)
            self.light_on_quarto.set(True)
            self.update_icons_for_all_rooms()

    def on_motion_hover_leave(self, event=None):
        self.motion.set(False)
        if self.mode.get() == "Automático":
            self.light_on_sala_estar.set(False)
            self.light_on_quarto.set(False)
            self.update_icons_for_all_rooms()

    # Redefinir todos os atuadores para desligado (apenas no modo Manual)
    def reset_actuators(self):
        if self.mode.get() == "Manual":
            self.light_on_sala_estar.set(False)
            self.light_on_cozinha.set(False)
            self.light_on_quarto.set(False)
            self.light_on_banheiro.set(False)
            self.ac_on_sala_estar.set(False)
            self.ac_on_quarto.set(False)
            self.update_icons_for_all_rooms()

    # Atualizar estados dos widgets com base no modo (desabilitar controles manuais no automático)
    def on_mode_change(self, *args):
        mode = self.mode.get()
        widgets = [
            self.light_sala_estar_check,
            self.light_cozinha_check,
            self.light_quarto_check,
            self.light_banheiro_check,
            self.ac_sala_estar_check,
            self.ac_quarto_check,
            self.reset_button
        ]
        if mode == "Automático":
            for w in widgets:
                w.state(['disabled'])
        else:
            for w in widgets:
                w.state(['!disabled'])
            self.reset_actuators()

    def update_sensors(self):
        while self.running:
            new_temp = round(random.uniform(18, 35), 1)
            new_humidity = round(random.uniform(30, 70), 1)
            self.root.after(0, self.temperature.set, new_temp)
            self.root.after(0, self.humidity.set, new_humidity)
            update_time_str = time.strftime("%Y-%m-%d %H:%M:%S")
            self.root.after(0, self.last_updated_label.config, {'text': f"Última atualização: {update_time_str}"})
            time.sleep(2)

    def automatic_control(self):
        while self.running:
            if self.mode.get() == "Automático":
                # Controlar AC na Sala de Estar e Quarto baseado na temperatura e movimento
                if self.temperature.get() > 28:
                    self.ac_on_sala_estar.set(True)
                    # Ativa AC do quarto somente se a luz do quarto estiver ligada (presença)
                    self.ac_on_quarto.set(self.light_on_quarto.get())
                else:
                    self.ac_on_sala_estar.set(False)
                    self.ac_on_quarto.set(False)

                self.root.after(0, self.update_icons_for_all_rooms)
            time.sleep(0.5)

    def stop(self):
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    ttk.Style().theme_use('clam')
    app = SmartHome(root)
    try:
        root.mainloop()
    finally:
        app.stop()