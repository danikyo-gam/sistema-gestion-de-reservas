from Clases import Sistema, Usuario, Admin, Vuelo, Reserva, Fecha, Pasajero
sistema = Sistema()
sistema.cargarInfo()
usuario_actual = None
admin_actual = None
modo_actual = None
vuelo_seleccionado_id = None
vuelo_seleccionado = None


import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageSequence
import os  
import sys
# Ruta al dll de VLC
vlc_path = r"C:\Program Files\VideoLAN\VLC"
os.add_dll_directory(vlc_path)
import vlc
import time
import ttkbootstrap as ttk

#escena 1 (inicio)
#escena 2 (aviso legal)
#escena 3 (lugares para viajar)
#escena 4 (Ciudad Goron)
#escena 6 (Desierto Gerudo)
#escena 5 (Dominio Zora)
#escena 7 (Aldea orni)
#escena 8 (Castillo de Hyrule)
#escena 9 (Aldea Kakariko)(disponible proximamente)
#escena 10 (Lago Hylia)(disponible proximamente)
#escena 11 (registro)
#escena 12 (login usuario)
#escena 13 (panel usuario)
#escena 14 (RESERVAR VUELO)
#escena 15 (MIS RESERVAS)
#escena 16 (modificar reserva)
#escena 17 (eliminar reserva)
#escena 18 (millas)
#escena 19 (editar perfil)
#escena 20 (realizar check-in)
#escena 21 (admin login)
#escena 22 (panel admin)
# ================================
#FUNCIONES GENERALES
# ================================

def calcular_estadisticas():
    stats = {
        "total_reservas": 0,
        "total_usuarios": len(sistema.verUsuarios()),
        "total_vuelos": len(sistema.verVuelos()),
        "vuelo_popular": "—"
    }

    vuelo_contador = {}

    try:
        with open("reservas.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")

                # Asegurar que tenga suficientes columnas
                if len(datos) < 12:
                    continue

                stats["total_reservas"] += 1
                id_vuelo = datos[2]

                vuelo_contador[id_vuelo] = vuelo_contador.get(id_vuelo, 0) + 1

    except FileNotFoundError:
        pass

    # Encontrar el vuelo más reservado
    if vuelo_contador:
        mas_popular = max(vuelo_contador, key=vuelo_contador.get)
        stats["vuelo_popular"] = mas_popular

    return stats

def actualizar_estadisticas():
    stats = calcular_estadisticas()

    stats_total_usuarios.set(stats["total_usuarios"])
    stats_total_vuelos.set(stats["total_vuelos"])
    stats_total_reservas.set(stats["total_reservas"])
    stats_vuelo_popular.set(stats["vuelo_popular"])

def abrir_cancelacion_usuario():
    if not seleccionar_reserva_para_cancelar():
        return

    cargar_datos_cancelacion()
    cambiar_escena(escena18)

def seleccionar_reserva_para_cancelar():
    seleccion = tabla_reservas_usuario.selection()
    if not seleccion:
        messagebox.showerror("Error", "Debe seleccionar una reserva.")
        return False

    valores = tabla_reservas_usuario.item(seleccion[0], "values")
    rid = valores[0]    
    estado = valores[5]   

 
    reserva_seleccionada.set(rid)


    if estado.lower() == "check-in":
        messagebox.showerror(
            "Operación no permitida",
            "No es posible cancelar una reserva que ya tiene Check-in realizado."
        )
        return False

    if estado.lower() == "cancelada":
        messagebox.showerror(
            "Operación no permitida",
            "La reserva ya está cancelada."
        )
        return False

    return True

def cargar_datos_cancelacion():
    """Carga datos de la reserva seleccionada en escena18."""
    rid = reserva_seleccionada.get().strip()

    if rid == "":
        datos_cancel.config(text="Vuelo: —   |   Día: —   |   Sillas: —")
        return

    reserva = sistema.buscarReserva(rid)
    if reserva is None:
        datos_cancel.config(text="Vuelo: —   |   Día: —   |   Sillas: —")
        return

    vuelo = sistema.buscarVuelo(reserva.getIdVuelo())

    if vuelo:
        fecha = vuelo.getFecha()
        fecha_txt = f"{fecha.getDD():02d}/{fecha.getMM():02d}/{fecha.getAA()} {fecha.getHH():02d}:{fecha.getMIN():02d}"
        destino = vuelo.getCiudadDestino()
    else:
        fecha_txt = "—"
        destino = "—"

    datos_cancel.config(
        text=f"Vuelo: {reserva.getIdVuelo()} → {destino}   |   Día: {fecha_txt}   |   Sillas: {reserva.getCantidadSillas()}"
    )
def cancelar_reserva():
    rid = reserva_seleccionada.get().strip()

    if rid == "":
        messagebox.showerror("Error", "No se seleccionó una reserva.")
        return

    reserva = sistema.buscarReserva(rid)
    if reserva is None:
        messagebox.showerror("Error", "La reserva no existe.")
        return

    # Confirmación del usuario
    if not messagebox.askyesno("Confirmar cancelación",
                               "¿Seguro que desea cancelar esta reserva?\nEsta acción no se puede deshacer."):
        return

    # MARCAR COMO CANCELADA
    reserva.setEstado("2")   # 2 = Cancelada

    # DEVOLVER SILLAS AL VUELO
    vuelo = sistema.buscarVuelo(reserva.getIdVuelo())
    if vuelo:
        if reserva.getTipoSilla() == "preferencial":
            vuelo.setSillasPref(vuelo.getSillasPref() + reserva.getCantidadSillas())
        else:
            vuelo.setSillasEco(vuelo.getSillasEco() + reserva.getCantidadSillas())

    # GUARDAR EN TXT
    sistema.guardarInfo()

    # ACTUALIZAR TABLA
    cargar_reservas_usuario_tabla()

    messagebox.showinfo("Reserva cancelada", "La reserva ha sido cancelada exitosamente.")

    cambiar_escena(escena15)


def seleccionar_reserva_para_modificar():
    """Obtiene la reserva seleccionada en tabla_reservas_usuario y carga sus datos en escena 17."""
    seleccion = tabla_reservas_usuario.selection()

    if not seleccion:
        messagebox.showerror("Error", "Debe seleccionar una reserva para modificar.")
        return

    rid = tabla_reservas_usuario.item(seleccion[0], "values")[0]
    reserva_seleccionada.set(rid)

    reserva = sistema.buscarReserva(rid)
    if reserva is None:
        messagebox.showerror("Error", "No se encontró la reserva.")
        return

    vuelo = sistema.buscarVuelo(reserva.getIdVuelo())

    # Mostrar datos actuales
    texto = f"Vuelo: {vuelo.getId()}   |   Día actual: {vuelo.getFecha()}   |   Sillas: {reserva.getCantidadSillas()}"
    datos_mod.config(text=texto)

    # Cargar valores actuales en inputs
    sillas_mod_var.set(reserva.getCantidadSillas())
    tipo_asiento_var.set("Preferencial" if reserva.getTipoSilla() == "preferencial" else "Económico")

    # Día actual (extraemos día en texto)
    dia_actual = vuelo.getFecha().getDiaSemana().upper() if hasattr(vuelo.getFecha(), "getDiaSemana") else ""
    if dia_actual in dias_semana:
        dia_mod_var.set(dia_actual)

    cambiar_escena(escena17)


def aplicar_cambios_reserva():
    """Aplica la modificación a la reserva seleccionada y guarda en TXT."""
    rid = reserva_seleccionada.get()
    reserva = sistema.buscarReserva(rid)

    if reserva is None:
        messagebox.showerror("Error", "No se encontró la reserva seleccionada.")
        return

    vuelo = sistema.buscarVuelo(reserva.getIdVuelo())

    # ============================================
    #   LEER NUEVOS VALORES
    # ============================================
    nuevas_sillas = sillas_mod_var.get()
    nuevo_tipo = tipo_asiento_var.get().lower()
    nuevo_dia = dia_mod_var.get()

    if nuevo_tipo not in ["preferencial", "económico", "económica"]:
        messagebox.showerror("Error", "Seleccione un tipo de asiento válido.")
        return

    # Normalizar
    if nuevo_tipo.startswith("econ"):
        nuevo_tipo = "economica"

    # ============================================
    #   VALIDAR DISPONIBILIDAD DE SILLAS
    # ============================================
    if nuevo_tipo == "preferencial":
        disponibles = vuelo.getSillasPref()
    else:
        disponibles = vuelo.getSillasEco()

    if nuevas_sillas > disponibles:
        messagebox.showerror("Error",
                             f"No hay suficientes sillas disponibles.\nSillas disponibles: {disponibles}")
        return

    # ============================================
    #   MODIFICAR OBJETO RESERVA
    # ============================================
    reserva.setCantidadSillas(nuevas_sillas)
    reserva.setTipoSilla(nuevo_tipo)

    # Modificar día del vuelo si tu clase Fecha lo permite
    # Si tu clase Fecha usa DD-MM-AA-HH-MM, deberíamos ajustar solo el día de semana.
    # Por ahora solo guardamos la intención textual en el label:
    nueva_fecha_txt = f"{nuevo_dia} - {vuelo.getFecha()}"
    texto_pasajeros = entrada_pasajeros_mod.get("1.0", tk.END).strip()

    if texto_pasajeros == "":
        messagebox.showerror("Error", "Debe ingresar al menos un pasajero.")
        return

    lineas = texto_pasajeros.split("\n")
    nuevos_pasajeros = []

    for ln in lineas:
        try:
            nombre, doc = ln.split("-")
            nombre = nombre.strip()
            doc = int(doc.strip())
            nuevos_pasajeros.append(Pasajero(nombre, doc))
        except:
            messagebox.showerror("Error", "Formato inválido en pasajeros.\nUse: Nombre - Documento")
            return

    # Reemplazar en la reserva
    reserva.setPasajeros(nuevos_pasajeros)
    
    sistema.guardarInfo()

    cargar_reservas_usuario_tabla()

    messagebox.showinfo("Éxito", "La reserva fue modificada correctamente.")

    cambiar_escena(escena15)

def abrir_checkin_usuario():
    seleccionar_reserva()          # Guarda el código en reserva_seleccionada
    cargar_datos_checkin()         # Llena los datos en escena16
    cambiar_escena(escena16)       # Cambia de escena sí o sí

def confirmar_checkin():
    rid = reserva_seleccionada.get()
    reserva = sistema.buscarReserva(rid)

    if reserva is None:
        messagebox.showerror("Error", "Reserva no encontrada.")
        return

    vuelo = sistema.buscarVuelo(reserva.getIdVuelo())

    # ===============================
    #  EQUIPAJE
    # ===============================
    equipaje_mano = mano_var.get()
    equipaje_cabina = cabina_var.get()
    equipaje_bodega = bodega_var.get()

    tipo_silla = reserva.getTipoSilla()

    costo_cabina = 0
    if tipo_silla == "economica" and equipaje_cabina > 0:
        costo_cabina = equipaje_cabina * 40000

    # Bodega depende del proyecto (aquí ejemplo)
    costo_bodega = equipaje_bodega * 50000  

    total_equipaje = costo_cabina + costo_bodega

    # ===============================
    # CAMBIAR ESTADO
    # ===============================
    reserva.setEstado("1")   # 1 = Check-in

    # ===============================
    # GUARDAR MILLAS
    # ===============================
    usuario_actual.acumularMillas(500)

    # ===============================
    # GUARDAR EN TXT
    # ===============================
    actualizar_estado_checkin_txt(rid)
    messagebox.showinfo("Check-In exitoso",
                        f"Check-In realizado.\n"
                        f"Costo equipaje: ${total_equipaje:,}\n"
                        f"Millas acumuladas: {usuario_actual.getMillas()}")

    cargar_reservas_usuario_tabla()
    cambiar_escena(escena15)

def actualizar_estado_checkin_txt(id_reserva):
    lineas = []
    with open("reservas.txt", "r", encoding="utf-8") as f:
        for linea in f:
            datos = linea.strip().split(",")

            if datos[0] == id_reserva:
                # Cambiar estado a "1" = Check-in
                datos[11] = "Check-in"
                linea = ",".join(datos) + "\n"
            else:
                linea = linea.strip() + "\n"

            lineas.append(linea)

    with open("reservas.txt", "w", encoding="utf-8") as f:
        f.writelines(lineas)


def cargar_datos_checkin():
    codigo = reserva_seleccionada.get().strip()
    print("DEBUG cargando check-in para reserva:", codigo)

    if codigo == "":
        datos_reserva.config(text="Vuelo: —   |   Día: —   |   Sillas: —")
        return

    with open("reservas.txt", "r", encoding="utf-8") as f:
        for linea in f:
            datos = linea.strip().split(",")

            if len(datos) < 12:
                continue

            if datos[0] == codigo:
                id_vuelo = datos[2]
                cantidad = datos[5]

                vuelo = sistema.buscarVuelo(id_vuelo)

                if vuelo:
                    fecha = vuelo.getFecha()
                    destino = vuelo.getCiudadDestino()

                    # ← ESTA ES LA LÍNEA CORRECTA
                    fecha_txt = f"{fecha.getDD():02d}/{fecha.getMM():02d}/{fecha.getAA()}  {fecha.getHH():02d}:{fecha.getMIN():02d}"
                else:
                    fecha_txt = "—"
                    destino = "—"

                datos_reserva.config(
                    text=f"Vuelo: {id_vuelo} → {destino}   |   Fecha: {fecha_txt}   |   Sillas: {cantidad}"
                )

                # resets
                mano_var.set(1)
                cabina_var.set(0)
                bodega_var.set(0)

                return

def abrir_checkin():
    seleccionado = tabla_reservas_usuario.focus()
    if not seleccionado:
        messagebox.showerror("Error", "Debe seleccionar una reserva.")
        return

    datos = tabla_reservas_usuario.item(seleccionado, "values")
    reserva_seleccionada.set(datos[0])  # ID de la reserva

    cargar_datos_checkin()
    cambiar_escena(escena16)

def cargar_reservas_usuario_tabla():
    tabla_reservas_usuario.delete(*tabla_reservas_usuario.get_children())

    usr_id = str(usuario_actual.getId()).strip()
    print("CARGANDO RESERVAS PARA USUARIO:", usr_id)

    try:
        vuelos = {}
        with open("vuelos.txt", "r", encoding="utf-8") as f:
            for linea in f:
                d = linea.strip().split(",")
                if len(d) >= 7:
                    codigo = d[0]
                    origen = d[1]
                    destino = d[2]
                    fecha = d[3]   # DD-MM-AAAA-HH-MM

                    try:
                        dd, mm, aa, hh, mn = fecha.split("-")
                        fecha_limpia = f"{dd}/{mm}/{aa}  {hh}:{mn}"
                    except:
                        fecha_limpia = "—"

                    vuelos[codigo] = {
                        "origen": origen,
                        "destino": destino,
                        "fecha": fecha_limpia
                    }

        with open("reservas.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")

                if len(datos) != 12:
                    continue

                id_res = datos[0]
                id_user = datos[1].strip()
                id_vuelo = datos[2]
                cantidad = datos[5]
                estado_raw = datos[11]

                if id_user != usr_id:
                    continue

                estados = {
                    "0": "Activa",
                    "1": "Check-In",
                    "2": "Cancelada"
                }
                estado = estados.get(estado_raw, estado_raw)

                destino = vuelos.get(id_vuelo, {}).get("destino", "—")
                fecha   = vuelos.get(id_vuelo, {}).get("fecha", "—")

                fila = (id_res, id_vuelo, destino, fecha, cantidad, estado)
                print("INSERTANDO EN TABLA USUARIO:", fila)
                tabla_reservas_usuario.insert("", "end", values=fila)

    except Exception as e:
        messagebox.showerror("Error", f"No fue posible cargar las reservas del usuario:\n{e}")

def confirmar_reserva():
    if vuelo_seleccionado.get() == "":
        messagebox.showerror("Error", "No hay vuelo seleccionado.")
        return

    vuelo = sistema.buscarVuelo(vuelo_seleccionado.get())
    if vuelo is None:
        messagebox.showerror("Error", "El vuelo no existe.")
        return

    tipo = tipo_silla_var.get().lower()
    cant = cant_sillas_var.get()

    if tipo == "" or cant == 0:
        messagebox.showerror("Error", "Seleccione tipo y cantidad de sillas.")
        return

    texto = entrada_pasajeros.get("1.0", tk.END).strip()
    if texto == "":
        messagebox.showerror("Error", "Ingrese los pasajeros.")
        return

    lineas = texto.split("\n")
    if len(lineas) != cant:
        messagebox.showerror("Error", "La cantidad de pasajeros debe coincidir.")
        return

    pasajeros = []
    for ln in lineas:
        try:
            nombre, doc = ln.split("-")
            pasajeros.append(Pasajero(nombre.strip(), int(doc.strip())))
        except:
            messagebox.showerror("Error", "Formato inválido. Use: Nombre - Documento")
            return

    nueva = Reserva(
        id=f"R{len(sistema.verReservas()) + 1}",
        idUsuario=usuario_actual.getId(),
        idVuelo=vuelo.getId(),
        pasajeros=pasajeros,
        tipoSilla=tipo,
        cantidadSillas=cant,
        equipajeCabina=equip_cab_var.get(),
        equipajeBodega=equip_bod_var.get(),
        equipajeMano=equip_man_var.get()
    )

    ok = sistema.agregarReserva(nueva)
    if not ok:
        messagebox.showerror("Error", "No hay suficientes sillas disponibles.")
        return

    sistema.guardarInfo()
    cargar_reservas_usuario_tabla()

    messagebox.showinfo("Éxito", "Reserva creada correctamente.")
    cambiar_escena(escena15)



def abrir_mis_millas():
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesión.")
        return

    millas_var.set(f"Millas acumuladas: {usuario_actual.getMillas()}")

    cambiar_escena(escena19)


def abrir_editar_perfil():
    if not usuario_actual:
        messagebox.showerror("Error", "No hay usuario cargado.")
        return

    usr_doc_var.set(usuario_actual.getId())
    usr_nombre_var.set(usuario_actual.getNombre())
    usr_correo_var.set(usuario_actual.getEmail())
    usr_pass_var.set(usuario_actual.getContrasena())

    cambiar_escena(escena20)

def login():
    global usuario_actual, modo_actual

    documento = doc_var.get().strip()
    contrasena = pass_var.get().strip()

    if not documento or not contrasena:
        login_msg_user.config(text="Ingrese documento y contraseña")
        return

    if not documento.isdigit():
        login_msg_user.config(text="Documento inválido")
        return

    documento = int(documento)

    user = sistema.buscarUsuario(documento)

    if user is None:
        login_msg_user.config(text="Usuario no encontrado")
        return

    if user.getContrasena() != contrasena:
        login_msg_user.config(text="Contraseña incorrecta")
        return


    login_msg_user.config(text="")
    usuario_actual = user
    modo_actual = "usuario"

    cargar_menu_usuario()
    cambiar_escena(escena13)
    reproducir_musica("musica_usuario.mp3")

def cargar_menu_usuario():
    try:
        lbl_bienvenida.config(text=f"Bienvenido, {usuario_actual.getNombre()}")
    except:
        pass

def intentar_login_Admin():
    global admin_actual, modo_actual
    documento = doc_admin_var.get().strip()
    contrasena = pass_admin_var.get()
    
    # VALIDAR ADMIN
    admin = sistema.buscarAdmin(int(documento))
    if admin is None or admin.getContrasena() != contrasena:
        login_msg.config(text="Usuario o contraseña inválidos")
        return
    
    admin_actual = admin
    modo_actual = "admin"
    
    cambiar_escena(escena22)
    reproducir_musica("admin_musica.mp3")

def volver_desde_escena32():
    if modo_actual == "usuario":
        cambiar_escena(escena14)
    else:
        cambiar_escena(escena28)

player_musica = None    
instancia_vlc = None
def reproducir_musica(ruta):
    global player_musica, instancia_vlc

    if instancia_vlc is None:
        instancia_vlc = vlc.Instance()

    if player_musica is None:
        player_musica = instancia_vlc.media_player_new()

    media = instancia_vlc.media_new(ruta)
    player_musica.set_media(media)
    player_musica.play()

    def verificar_loop():
        try:
            pos = player_musica.get_position()

            if pos > 0.98:
                player_musica.set_position(0)  
                player_musica.play()

        except:
            pass

        app.after(200, verificar_loop)

    verificar_loop()



def cambiar_escena(nueva_escena):
    nueva_escena.tkraise()

#Pantlla centrada
def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    sw= ventana.winfo_screenwidth()
    sh= ventana.winfo_screenheight() 
    x = (sw - ancho) // 2
    y = (sh - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

#Ventana emergente
def mostrar_mensaje():
    ventana_mensaje = tk.Toplevel(app)
    ventana_mensaje.iconbitmap("trifuerza.ico")
    ventana_mensaje.title("IMPORTANTE - Declaracion Legal")
    w, h = 900, 500
    centrar_ventana(ventana_mensaje, w, h)
    ventana_mensaje.resizable(False, False)

    ventana_mensaje.transient(app)
    ventana_mensaje.lift()
    ventana_mensaje.attributes('-topmost', True)
    ventana_mensaje.focus_force()
    ventana_mensaje.grab_set()
    gif = Image.open("aviso.gif")  
    
    frames = []
    for frame in ImageSequence.Iterator(gif):
        frame = frame.resize((w, h))   
        frames.append(ImageTk.PhotoImage(frame))

    fondo = tk.Label(ventana_mensaje)
    fondo.place(x=0, y=0, relwidth=1, relheight=1)

    def animar(i=0):
        fondo.config(image=frames[i])
        ventana_mensaje.after(50, animar, (i+1) % len(frames))
    animar()

    texto = (
        "Declaración Legal\n\n"
        "El presente proyecto ha sido desarrollado como parte de un trabajo académico sin fines comerciales. "
        "Algunas imágenes, ilustraciones y elementos visuales utilizados en este documento y en la aplicación "
        "asociada proceden de fuentes externas y siguen siendo propiedad de sus respectivos autores y titulares de derechos.\n\n"
        "La franquicia The Legend of Zelda, así como cualquier contenido relacionado, es propiedad intelectual de Nintendo. "
        "No se reclama ningún derecho sobre dicho material.\n\n"
        "El uso de estos recursos se realiza exclusivamente con fines educativos, de aprendizaje y demostración técnica. "
        "No se pretende infringir derechos de autor ni distribuir, comercializar o utilizar el material con otro propósito distinto al académico."
    )

    info = tk.Label(
        ventana_mensaje,
        text=texto,
        font=("Triforce", 14),
        fg="white",
        bg="#000080",
        wraplength=700,
        justify="left"
    )
    info.place(relx=0.5, rely=0.5, anchor="center")

    continuar = ttk.Button(
        ventana_mensaje,
        text="Continuar",
        style="Rojo.TButton",
        command=ventana_mensaje.destroy,
    )
    continuar.place(relx=0.5, rely=0.9, anchor="center")

    ventana_mensaje.after(100, lambda: ventana_mensaje.attributes('-topmost', False))
    app.wait_window(ventana_mensaje)

# ---------------------------
#   VENTANA PRINCIPAL
# ---------------------------

app = ttk.Window(themename="superhero")
app.iconbitmap("trifuerza.ico")


style = ttk.Style()
reserva_seleccionada = tk.StringVar()
vuelo_seleccionado = tk.StringVar() 
usuario_actual = None 
style.configure(
    "Verde.TButton",
    font=("Triforce", 14, "bold"),
    background="#2E8B57",
    foreground="white"
)

style.configure(
    "Rojo.TButton",
    font=("Triforce", 14, "bold"),
    background="#8B0000",
    foreground="white"
)

style.configure(
    "Azul.TButton",
    font=("Triforce", 14, "bold"),
    background="#1E4C7A",
    foreground="white"
)
app.title("Sistema de reservas de la aerolinea")
main_w, main_h = 1200, 675
centrar_ventana(app, main_w, main_h)


fondo_img = Image.open("inicio.jpg")
fondo_img = fondo_img
fondo_tk = ImageTk.PhotoImage(fondo_img)
escena1 = ttk.Frame(app)
escena1.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_label = tk.Label(escena1, image=fondo_tk)
fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
escena1.fondo_tk = fondo_tk

titulo = ttk.Label(escena1, text="Bienvenido al sistema de reservas de la areolina", font=("Triforce",24))
titulo.place(relx=0.5, rely=0.22, anchor="center")

sub = ttk.Label(escena1, text="Desde la montaña de la muerte hasta el desierto gerudo", font=("Albw Botw Hylian", 10))
sub.place(relx=0.5, rely=0.27, anchor="center")

autores = ttk.Label(escena1, text="Dani Juli Samu", font=("Botw Sheikah", 10))
autores.place(relx=1.0, rely=1.0, anchor="se")

style.configure(
    "Importante.TButton",
    font=("Triforce", 18, "bold"),
    foreground="white",
    background="#D4AF37",
    borderwidth=3,
    relief="raised"
)
importante = ttk.Button(
    escena1,
    text="IMPORTANTE",
    style="Importante.TButton",
    command=lambda: cambiar_escena(escena2)
)
importante.place(relx=0.8, rely=0.84, anchor="center")

style.configure(
    "Salir.TButton",
    font=("Triforce", 18, "bold"),
    foreground="white",
    background="#8B0000",
    borderwidth=3,
    relief="raised"
)

salir = ttk.Button(
    escena1,
    text="Salir",
    style="Salir.TButton",
    command=app.destroy
)
salir.place(relx=0.20, rely=0.88, anchor="center")

salir.place(relx=0.2, rely=0.84, anchor= "center")

style.configure(
    "Destinos.TButton",
    font=("Triforce", 18, "bold"),
    foreground="white",
    background="#1E56A0",
    borderwidth=3,
    relief="raised"
)

lugares = ttk.Button(
    escena1,
    text="Conoce nuestros destinos",
    style="Destinos.TButton",
    command=lambda: cambiar_escena(escena3)
)
lugares.place(relx=0.5, rely=0.4, anchor="center")

style.configure(
    "Register.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#D4AF37"     
)
style.configure(
    "Login.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#16304C"      
)
btn_login = ttk.Button(
    escena1,
    text="Ingresa a tu cuenta",
    style="Login.TButton",
    command=lambda: cambiar_escena(escena12)
)
btn_login.place(relx=0.5, rely=0.5, anchor="center")

btn_register = ttk.Button(
    escena1,
    text="Registrarse",
    style="Register.TButton",
    command=lambda: cambiar_escena(escena11)
)
btn_register.place(relx=0.5, rely=0.58, anchor="center")

logigin_admin = ttk.Button(
    escena1,
    text="Administrador",
    style="Login.TButton",
    command=lambda: cambiar_escena(escena21)
)
logigin_admin.place(relx=0.5, rely=0.66, anchor="center")

#//////////
#Fin de la escena 1
#//////////////////

#Escena 2
escena2 = ttk.Frame(app)
escena2.place(relx=0, rely=0, relwidth=1, relheight=1)


gif = Image.open("aviso.gif")  
w, h = 1511, 850
frames = []
for frame in ImageSequence.Iterator(gif):
        frame = frame.resize((w, h))   
        frames.append(ImageTk.PhotoImage(frame))

fondo = tk.Label(escena2)
fondo.place(x=0, y=0, relwidth=1, relheight=1)

def animar(i=0):
        fondo.config(image=frames[i])
        escena2.after(50, animar, (i+1) % len(frames))
animar()
contenedor = tk.Frame(escena2)
contenedor.place(relx=0.5, rely=0.1, anchor="n") 
     
text=(
   "Declaración Legal\n\n"
    "El presente proyecto ha sido desarrollado como parte de un trabajo académico sin fines comerciales. "
    "Algunas imágenes, ilustraciones y elementos visuales utilizados en este documento y en la aplicación "
    "asociada proceden de fuentes externas y siguen siendo propiedad de sus respectivos autores y titulares de derechos.\n\n"
    "La franquicia The Legend of Zelda, así como cualquier contenido relacionado, es propiedad intelectual de Nintendo. "
    "No se reclama ningún derecho sobre dicho material.\n\n"
    "El uso de estos recursos se realiza exclusivamente con fines educativos, de aprendizaje y demostración técnica. "
    "No se pretende infringir derechos de autor ni distribuir, comercializar o utilizar el material con otro propósito distinto al académico.")
info = tk.Label(
        contenedor,
        text=text,
        font=("Triforce", 14),
        fg="white",
        bg="#000080",
        wraplength=700,
        justify="left"
    )
info.pack(pady=(0,20))


style.configure(
    "Volver.TButton",
    font=("Triforce", 16, "bold")
)

volver = tk.Button(
    escena2,
    text="Volver al inicio",
    font=("Triforce", 16, "bold italic"),
    command=lambda: cambiar_escena(escena1)
)
volver.place(relx=0.5, rely=0.74, anchor="center")
#////////////////
#Fin escena 2
#///////////////

#escena 3 (lugares para viajar)
escena3 = ttk.Frame(app)
escena3.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo3_img = Image.open("mapa.jpg")
fondo3_tk = ImageTk.PhotoImage(fondo3_img)
fondo3_label = tk.Label(escena3, image=fondo3_tk, bg="white")
fondo3_label.place(x=0, y=0, relwidth=1, relheight=1)
escena3.fondo3_tk = fondo3_tk

style.configure(
    "MiBoton.TButton",
    font=("Triforce", 16, "bold italic"),
    foreground="white",
    background="#265C42"
)
btn_volver = ttk.Button(
    escena3,
    text="Volver al inicio",
    style="MiBoton.TButton",
    command=lambda: cambiar_escena(escena1)
)
btn_volver.place(relx=0.9, rely=0.93, anchor="center")
btn_volver.tkraise()

style.configure(
     "Goron.TButton",
        font=("Triforce", 14, "bold"),
        background="#B22222",
        foreground="white"
)
ciudad_goron = ttk.Button(
    escena3,
    text="Ciudad Goron",
    style="Goron.TButton",
    command=lambda: (
         cambiar_escena(escena4),
            reproducir_musica("Daruk_theme.mp3")
         )
)
ciudad_goron.place(relx=0.7, rely=0.23, anchor="center")

style.configure(
    "Gerudo.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#C89F59"
)
desierto_gerudo = ttk.Button(
    escena3,
    text="Desierto Gerudo",
    style="Gerudo.TButton",
    command=lambda: (
        cambiar_escena(escena5),
        reproducir_musica("Urbosa_theme.mp3")
        )
)
desierto_gerudo.place(relx=0.2, rely=0.83, anchor="center")

style.configure(
    "Zora.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#1E90FF"
)

dominio_zora = ttk.Button(
    escena3,
    text="Dominio Zora",
    style="Zora.TButton",
    command=lambda: (
        cambiar_escena(escena6),
        reproducir_musica("Mipha_theme.mp3"))
)
dominio_zora.place(relx=0.8, rely=0.43, anchor="center")

style.configure(
     "Orni.TButton",
        font=("Triforce", 16, "bold"),
        foreground="white",
        background="#4ED3F1"
)
aldea_orni = ttk.Button(
    escena3,
    text="Aldea Orni",
    style="Orni.TButton",
    command=lambda: (
        cambiar_escena(escena7),
        reproducir_musica("Revali_theme.mp3")
    )
)
aldea_orni.place(relx=0.2, rely=0.3, anchor="center")
style.configure(
    "Hyrule.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#D4AF37"
)
castillo_hyrule = ttk.Button(
    escena3,
    text="Castillo de Hyrule",
    style="Hyrule.TButton",
    command=lambda: (
        cambiar_escena(escena8),
        reproducir_musica("Zelda_theme.mp3"))
)
castillo_hyrule.place(relx=0.5, rely=0.4, anchor="center")
style.configure(
    "Kakariko.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#4C7A46"
)
btn_kakariko = ttk.Button(
    escena3,
    text="Aldea Kakariko",
    style="Kakariko.TButton",
    command=lambda: (cambiar_escena(escena9), reproducir_musica("kakariko_theme.mp3"))                  
)

btn_kakariko.place(relx=0.7, rely=0.55, anchor="center")

style.configure(
    "Hylia.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#3FA7D6"
)
btn_hylia = ttk.Button(
    escena3,
    text="Lago Hylia",
    style="Hylia.TButton",
    command=lambda: (cambiar_escena(escena10), reproducir_musica("lago.mp3"))
)
btn_hylia.place(relx=0.48, rely=0.73, anchor="center")

#//////////////
#Fin escena 3
#/////////////////


# ================================
#   ESCENA 4 — CIUDAD GORON
# ================================
escena4 = ttk.Frame(app)
escena4.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_goron_img = Image.open("Goron.jpg") 
fondo_goron_tk = ImageTk.PhotoImage(fondo_goron_img)
fondo_goron_label = tk.Label(escena4, image=fondo_goron_tk)
fondo_goron_label.place(x=0, y=0, relwidth=1, relheight=1)
escena4.fondo_goron_tk = fondo_goron_tk
style.configure(
    "VolverGoron.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#B22222"
)

titulo_goron = tk.Label(
    escena4,
    text="CIUDAD GORON – HOGAR DEL CAMPEÓN DARUK",
    font=("Triforce", 22, "bold"),
    fg="white",
    bg="#7A1F1F",   
    padx=20,
    pady=10
)
titulo_goron.place(relx=0.5, rely=0.06, anchor="center")

texto_goron = (
    "Entre el calor del magma y las imponentes laderas de la Montaña de la Muerte, "
    "se encuentra Ciudad Goron, una fortaleza natural donde el fuego nunca descansa.\n\n"
    "Este es el hogar del valiente y poderoso campeón Daruk, recordado por su imponente fuerza, "
    "su espíritu protector y su leal corazón. Su valentía ayudó a defender al reino en tiempos oscuros, "
    "y su legado aún resuena entre los rugidos de la montaña.\n\n"
    "Viajar a Ciudad Goron es adentrarse en una cultura forjada en roca y lava, "
    "donde cada Goron se enorgullece de su coraje y determinación.\n\n"
    "Explora sus caminos ardientes, descubre su fortaleza natural y déjate inspirar "
    "por la determinación del gran Daruk.\n\n"
    "¡Te damos la bienvenida a Ciudad Goron!"
)
texto_goron_label = tk.Label(
    escena4,
    text=texto_goron,
    font=("RocknRoll One", 12),
    fg="white",
    bg="#7A1F1F",   
    wraplength=750,
    justify="center",
    padx=20,
    pady=20
)
texto_goron_label.place(relx=0.5, rely=0.50, anchor="center")

btn_volver_goron = ttk.Button(
    escena4,
    text="Volver",
    style="VolverGoron.TButton",
    command=lambda: (cambiar_escena(escena3), reproducir_musica("musica_incio.mp3"))
)
btn_volver_goron.place(relx=0.5, rely=0.95, anchor="center")
#Fin de escena 4

#================================
#   ESCENA 6 - DOMINIO ZORA
#================================
escena6 = ttk.Frame(app)
escena6.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_zora_img = Image.open("mipha.png")
fondo_zora_tk = ImageTk.PhotoImage(fondo_zora_img)
fondo_zora_label = tk.Label(escena6, image=fondo_zora_tk)
fondo_zora_label.place(x=0, y=0, relwidth=1, relheight=1)
escena6.fondo_zora_tk = fondo_zora_tk
style.configure(
    "VolverZora.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#1D8EFF"
)
titulo_zora = tk.Label(
    escena6,
    text="DOMINIO ZORA – EL LEGADO DE LA PRINCESA MIPHA",
    font=("Triforce", 22, "bold"),
    fg="white",
    bg="#1E3D5A",  
    padx=20,
    pady=10
)
texto_zora = (
    "En lo más profundo de las tierras acuosas de Hyrule se alza el majestuoso Dominio Zora,\n"
    "un santuario cristalino donde el agua fluye eterna y la armonía gobierna cada rincón.\n\n"
    "Este es el hogar de la princesa Mipha, recordada no solo por su dulzura y compasión,\n"
    "sino también por su poder sanador y su lealtad como una de los campeones elegidos.\n\n"
    "Su valentía y sacrificio dejaron una huella imborrable en el corazón de su pueblo, y aún hoy,\n"
    "las aguas del dominio parecen susurrar el recuerdo de su espíritu noble y protector.\n\n"
    "Viajar al Dominio Zora es sumergirse en serenidad y luz, atravesar puentes resplandecientes\n"
    "y contemplar la belleza del lugar que vio crecer a la incomparable princesa Mipha.\n\n"
    "¡Bienvenido al hogar de la guardiana del agua y la esperanza de Hyrule!"
)
texto_zora_label = tk.Label(
    escena6,
    text=texto_zora,
    font=("RocknRoll One", 11),
    fg="white",
    bg="#1E3D5A",   
    wraplength=900,
    justify="center",
    padx=15,
    pady=15
)
texto_zora_label.place(relx=0.5, rely=0.50, anchor="center")

titulo_zora.place(relx=0.5, rely=0.1, anchor="center")
btn_volver_zora = ttk.Button(
    escena6,
    text="Volver",
    style="VolverZora.TButton",
    command=lambda: (cambiar_escena(escena3), reproducir_musica("musica_incio.mp3"))
)
btn_volver_zora.place(relx=0.5, rely=0.9, anchor="center")
#Fin de escena 6

# ================================
#   ESCENA 5 - DESIERTO GERUDO
# ================================
escena5 = ttk.Frame(app)
escena5.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_gerudo_img = Image.open("gerudo.jpeg")
fondo_gerudo_tk = ImageTk.PhotoImage(fondo_gerudo_img)
fondo_gerudo_label = tk.Label(escena5, image=fondo_gerudo_tk)
fondo_gerudo_label.place(x=0, y=0, relwidth=1, relheight=1)
escena5.fondo_gerudo_tk = fondo_gerudo_tk
style.configure(
    "VolverGerudo.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#C89F59"
)

titulo_gerudo = tk.Label(
    escena5,
    text="DESIERTO GERUDO – EL HONOR DE LA CAMPEONA URBOSA",
    font=("Triforce", 20, "bold"),
    fg="white",
    bg="#8A4B2A",   # Arena rojiza, muy Gerudo
    padx=20,
    pady=10
)
titulo_gerudo.place(relx=0.5, rely=0.06, anchor="center")

texto_gerudo = (
    "En los confines abrasadores del Desierto Gerudo, donde las dunas cantan con el viento\n"
    "y el sol marca cada sendero, se alza la orgullosa Ciudad Gerudo, cuna de un pueblo\n"
    "indomable y de una tradición tan antigua como Hyrule mismo.\n\n"
    "Este es el hogar de Urbosa, la imponente y noble campeona Gerudo, recordada por su\n"
    "fuerza deslumbrante, su increíble dominio del rayo y su inquebrantable lealtad hacia la\n"
    "princesa Zelda. Urbosa, con su valentía y gracia, defendió su reino con el honor que solo\n"
    "una verdadera líder puede portar.\n\n"
    "Caminar por el desierto es adentrarse en un territorio de misterio y resistencia, donde la\n"
    "determinación de su gente se refleja en cada muro de la ciudadela y en cada guardiana\n"
    "que vigila sus puertas.\n\n"
    "Descubre la fortaleza del espíritu Gerudo y déjate maravillar por el legado eléctrico y\n"
    "protector de la gran Urbosa.\n\n"
    "¡Bienvenido al reino de arena, sol y valor absoluto!"
)

texto_gerudo_label = tk.Label(
    escena5,
    text=texto_gerudo,
    font=("RocknRoll One", 11),
    fg="white",
    bg="#8A4B2A",
    wraplength=950,
    justify="center",
    padx=18,
    pady=18
)

texto_gerudo_label.place(relx=0.5, rely=0.50, anchor="center")

btn_volver_gerudo = ttk.Button(
    escena5,
    text="Volver",
    style="VolverGerudo.TButton",
    command=lambda: (cambiar_escena(escena3), reproducir_musica("musica_incio.mp3"))
)
btn_volver_gerudo.place(relx=0.5, rely=0.93, anchor="center")
#Fin de escena 5

# ================================
#   ESCENA 7 - ALDEA ORNI
#===============================
escena7 = ttk.Frame(app)
escena7.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_orni_img = Image.open("orni.png")
fondo_orni_tk = ImageTk.PhotoImage(fondo_orni_img)
fondo_orni_label = tk.Label(escena7, image=fondo_orni_tk)
fondo_orni_label.place(x=0, y=0, relwidth=1, relheight=1)
escena7.fondo_orni_tk = fondo_orni_tk

titulo_orni = tk.Label(
    escena7,
    text="ALDEA ORNI – LA DESTREZA DEL CAMPEÓN REVALI",
    font=("Triforce", 22, "bold"),
    fg="white",
    bg="#355C7D",    # Azul viento
    padx=20,
    pady=10
)
titulo_orni.place(relx=0.5, rely=0.06, anchor="center")

texto_orni = (
    "En las alturas escarpadas de la región de Tabanta se encuentra la Aldea Orni,\n"
    "un refugio suspendido entre montañas donde el viento es guía y compañero.\n\n"
    "Esta es la cuna de Revali, el campeón Orni, célebre por su incomparable destreza\n"
    "aérea y su habilidad con el arco. Su orgullo era tan grande como su talento, pero\n"
    "su valentía y determinación lo convirtieron en un símbolo de excelencia para su\n"
    "pueblo.\n\n"
    "Surcar los cielos junto a los Orni es experimentar libertad pura. Sus plataformas\n"
    "elevadas, su música melódica y el eterno soplo del viento hacen de esta aldea un\n"
    "lugar único en todo Hyrule.\n\n"
    "Visitar la Aldea Orni es contemplar el legado de Revali, un héroe cuya ambición\n"
    "y espíritu indomable elevaron a su pueblo a nuevas alturas.\n\n"
    "¡Bienvenido al hogar del viento y la precisión absoluta!"
)

texto_orni_label = tk.Label(
    escena7,
    text=texto_orni,
    font=("RocknRoll One", 11),
    fg="white",
    bg="#355C7D",
    wraplength=950,      
    justify="center",
    padx=18,
    pady=18
)
texto_orni_label.place(relx=0.5, rely=0.50, anchor="center")

style.configure(
    "VolverOrni.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#4ED3F1"
)
btn_volver_orni = ttk.Button(
    escena7,
    text="Volver",
    style="VolverOrni.TButton",
    command=lambda: (cambiar_escena(escena3), reproducir_musica("musica_incio.mp3"))
)   
btn_volver_orni.place(relx=0.5, rely=0.95, anchor="center")
#Fin de escena 7

# ================================
#   ESCENA 8 - CASTILLO DE HYRULE
#===============================
escena8 = ttk.Frame(app)
escena8.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_hyrule_img = Image.open("castillo.jpg")
fondo_hyrule_img = fondo_hyrule_img
fondo_hyrule_tk = ImageTk.PhotoImage(fondo_hyrule_img)
fondo_hyrule_label = tk.Label(escena8, image=fondo_hyrule_tk)
fondo_hyrule_label.place(x=0, y=0, relwidth=1, relheight=1)
escena8.fondo_hyrule_tk = fondo_hyrule_tk

titulo_label = tk.Label(
    escena8,
    text="CASTILLO DE HYRULE – CUNA DE LA FAMILIA REAL",
    font=("Triforce", 22, "bold"),
    fg="white",
    bg="#1A1A1A",    
    padx=20,
    pady=10
)

titulo_label.place(relx=0.5, rely=0.07, anchor="center")

texto_hyrule = (
    "Desde tiempos inmemoriales, el majestuoso Castillo de Hyrule se alza como el corazón del reino, "
    "símbolo de sabiduría, valor y poder.\n\n"
    "Sus murallas antiguas resguardan historias que han trascendido generaciones, y cada uno de sus pasillos "
    "conserva la esencia de la Familia Real, protectora eterna de Hyrule.\n\n"
    "Este viaje es una invitación a descubrir el legado de la princesa Zelda, una figura de nobleza y fortaleza, "
    "cuya determinación ha guiado al reino en los momentos más oscuros.\n\n"
    "Emprende tu viaje al corazón del reino.\n"
    "Conoce el hogar de la realeza.\n"
    "Descubre el Castillo de Hyrule."
)
texto_label = tk.Label(
    escena8,
    text=texto_hyrule,
    font=("RocknRoll One", 14),
    fg="white",
    bg="#1A1A1A",  
    wraplength=900, 
    justify="center"
)
texto_label.place(relx=0.5, rely=0.51, anchor="center")

style.configure(
    "VolverHyrule.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#D4AF37"
)   
btn_volver_hyrule = ttk.Button(
    escena8,
    text="Volver",
    style="VolverHyrule.TButton",
    command=lambda: (cambiar_escena(escena3), reproducir_musica("musica_incio.mp3"))
)
btn_volver_hyrule.place(relx=0.5, rely=0.92, anchor="center")
#Fin de escena 8
# ================================
#   ESCENA 9 - ALDEA KAKARIKO
escena9 = ttk.Frame(app)
escena9.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_kakariko_img = Image.open("kakariko.jpg")
fondo_kakariko_tk = ImageTk.PhotoImage(fondo_kakariko_img)
fondo_kakariko_label = tk.Label(escena9, image=fondo_kakariko_tk)
fondo_kakariko_label.place(x=0, y=0, relwidth=1, relheight=1)
escena9.fondo_kakariko_tk = fondo_kakariko_tk

titulo_kakariko = tk.Label(
    escena9,
    text="ALDEA KAKARIKO – EL SABER DE LA ANCESTRA IMPA",
    font=("Triforce", 22, "bold"),
    fg="white",
    bg="#2E3A56", 
    padx=20,
    pady=10
)
titulo_kakariko.place(relx=0.5, rely=0.09, anchor="center")

texto_kakariko = (
    "Oculta entre montañas y rodeada de tranquilidad espiritual, se encuentra la Aldea Kakariko,\n"
    "santuario ancestral del pueblo Sheikah y guardiana de secretos tan antiguos como Hyrule.\n\n"
    "En este lugar reside Impa, la sabia líder Sheikah, dedicada a preservar el conocimiento que\n"
    "por generaciones ha protegido al reino. Su serenidad, firmeza y profunda conexión con la\n"
    "princesa Zelda la convierten en una de las figuras más respetadas de toda la historia Hyliana.\n\n"
    "Caminar por las cuestas iluminadas por faroles, visitar las humildes casas de madera y sentir\n"
    "el susurro del viento entre los cerezos en flor es adentrarse en un remanso de paz espiritual.\n\n"
    "Kakariko es un símbolo de memoria, tradición y valentía silenciosa; un lugar donde cada paso\n"
    "parece llevar consigo la sabiduría de generaciones pasadas.\n\n"
    "¡Bienvenido a la aldea donde el tiempo se mueve con calma y la historia nunca se olvida!"
)

texto_kakariko_label = tk.Label(
    escena9,
    text=texto_kakariko,
    font=("RocknRoll One", 11),
    fg="white",
    bg="#2E3A56",
    wraplength=950,
    justify="center",
    padx=18,
    pady=18
)
texto_kakariko_label.place(relx=0.5, rely=0.50, anchor="center")

style.configure(
    "VolverKakariko.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#4C7A46"
)
btn_volver_kakariko = ttk.Button(
    escena9,
    text="Volver",
    style="VolverKakariko.TButton",
    command=lambda: (cambiar_escena(escena3), reproducir_musica("musica_incio.mp3"))
)
btn_volver_kakariko.place(relx=0.5, rely=0.92, anchor="center")
#Fin de escena 9    

# ================================
#   ESCENA 10 - LAGO HYLIA
escena10 = ttk.Frame(app)
escena10.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_hylia_img = Image.open("lago.jpg")
fondo_hylia_tk = ImageTk.PhotoImage(fondo_hylia_img)
fondo_hylia_label = tk.Label(escena10, image=fondo_hylia_tk)
fondo_hylia_label.place(x=0, y=0, relwidth=1, relheight=1)
escena10.fondo_hylia_tk = fondo_hylia_tk

titulo_hylia = tk.Label(
    escena10,
    text="LAGO HYLIA – EL ESPEJO SAGRADO DE LA DIOSA",
    font=("Triforce", 22, "bold"),
    fg="white",
    bg="#1E4C7A", 
    padx=20,
    pady=10
)
titulo_hylia.place(relx=0.5, rely=0.1, anchor="center")

texto_hylia = (
    "Extendido como un manto celestial en el corazón de Hyrule, el Lago Hylia es uno de los lugares\n"
    "más sagrados y emblemáticos del reino. Sus aguas tranquilas reflejan no solo el cielo, sino también\n"
    "las historias que han acompañado al pueblo desde tiempos remotos.\n\n"
    "El lago está profundamente ligado a la Diosa Hylia, protectora del mundo y símbolo de esperanza.\n"
    "Muchas leyendas afirman que sus bendiciones aún reposan en estas aguas, recordando la antigua\n"
    "conexión entre diosa y humanidad.\n\n"
    "Sus orillas ofrecen serenidad, sus horizontes despiertan inspiración y su atmósfera envuelve a cada\n"
    "visitante con una sensación de calma espiritual. Viajar al Lago Hylia es acercarse a uno de los\n"
    "rincones más puros y enigmáticos de todo Hyrule.\n\n"
    "¡Bienvenido al santuario natural donde el cielo y la tierra se encuentran en perfecta armonía!"
)

texto_hylia_label = tk.Label(
    escena10,
    text=texto_hylia,
    font=("RocknRoll One", 11),
    fg="white",
    bg="#1E4C7A",
    wraplength=950,
    justify="center",
    padx=18,
    pady=18
)
texto_hylia_label.place(relx=0.5, rely=0.50, anchor="center")

style.configure(
    "VolverHylia.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#3FA7D6"
)
btn_volver_hylia = ttk.Button(
    escena10,
    text="Volver",
    style="VolverHylia.TButton",
    command=lambda: (cambiar_escena(escena3), reproducir_musica("musica_incio.mp3"))
)
btn_volver_hylia.place(relx=0.5, rely=0.90, anchor="center")
#Fin de escena 10

#================================
# ESCENA 12 - LOGIN USUARIO
#================================
escena12 = ttk.Frame(app)
escena12.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_login_img = Image.open("usuario.jpg")
fondo_login_tk = ImageTk.PhotoImage(fondo_login_img)
fondo_login_label = tk.Label(escena12, image=fondo_login_tk)
fondo_login_label.place(x=0, y=0, relwidth=1, relheight=1)
escena12.fondo_login_tk = fondo_login_tk

titulo_login = ttk.Label(
    escena12,
    text="Iniciar Sesión",
    font=("Triforce", 32, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_login.place(relx=0.5, rely=0.28, anchor="center")

style.configure(
    "VolverLogin.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#16304C"
)
btn_volver_login = ttk.Button(
    escena12,
    text="Volver",
    style="VolverLogin.TButton",
    command=lambda: (cambiar_escena(escena1))
)
btn_volver_login.place(relx=0.5, rely=0.73, anchor="center")


doc_var = tk.StringVar()
pass_var = tk.StringVar()

label_doc = ttk.Label(escena12, text="Documento:", font=("Triforce", 14), foreground="white", background="#16304C")
label_doc.place(relx=0.38, rely=0.40, anchor="e")
entry_doc = ttk.Entry(escena12, textvariable=doc_var, width=30)
entry_doc.place(relx=0.40, rely=0.40, anchor="w")

label_pass = ttk.Label(escena12, text="Contraseña:", font=("Triforce", 14), foreground="white", background="#16304C")
label_pass.place(relx=0.38, rely=0.48, anchor="e")
entry_pass = ttk.Entry(escena12, textvariable=pass_var, width=30, show="*")
entry_pass.place(relx=0.40, rely=0.48, anchor="w")

login_msg_user = tk.Label(escena12, text="", font=("Triforce", 12), fg="red", bg="#16304C")
login_msg_user.place(relx=0.5, rely=0.64, anchor="center")


style.configure(
    "Ingresar.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#16304C"
)
btn_ingresar = ttk.Button(
    escena12,
    text="Ingresar",
    style="Ingresar.TButton",
    command=lambda: (login()
))
btn_ingresar.place(relx=0.5, rely=0.58, anchor="center")    
#Fin de escena 12
# ===============================
#  ESCENA 13 - PANEL USUARIO
# ===============================
escena13 = ttk.Frame(app)
escena13.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_panel_img = Image.open("menu.png")
fondo_panel_tk = ImageTk.PhotoImage(fondo_panel_img)
fondo_panel_label = tk.Label(escena13, image=fondo_panel_tk)
fondo_panel_label.place(x=0, y=0, relwidth=1, relheight=1)
escena13.fondo_panel_tk = fondo_panel_tk
style.configure(
    "VolverPanel.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#8B0000"
)
def cerrar_sesion():
    global usuario_actual
    usuario_actual = None
    cambiar_escena(escena1)
    reproducir_musica("musica_incio.mp3")

btn_volver_panel = ttk.Button(
    escena13,
    text="Cerrar sesión",
    style="VolverPanel.TButton",
    command= cerrar_sesion
)
btn_volver_panel.place(relx=0.5, rely=0.80, anchor="center")

style.configure(
    "Reservar.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#1E4C7A"
)
btn_reservar = ttk.Button(
    escena13,
    text="Reservar y buscar vuelos",
    style="Reservar.TButton",
    command=lambda: cambiar_escena(escena14)
)
btn_reservar.place(relx=0.5, rely=0.28, anchor="center")

style.configure(
    "MisReservas.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#1E4C7A"
)
btn_mis_reservas = ttk.Button(
    escena13,
    text="Mis reservas",
    style="MisReservas.TButton",
    command=lambda: (cargar_reservas_usuario_tabla(), cambiar_escena(escena15))
)
btn_mis_reservas.place(relx=0.5, rely=0.45, anchor="center")

style.configure(
    "MisMillas.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#D4AF37"
)
btn_millas = ttk.Button(
    escena13,
    text="Mis millas",
    style="MisMillas.TButton",
    command=abrir_mis_millas
)
btn_millas.place(relx=0.25, rely=0.62, anchor="center")

style.configure(
    "EditarPerfil.TButton",
    font=("Triforce", 16, "bold"),
    foreground="white",
    background="#3723D3"
)
btn_editar_perfil = ttk.Button(
    escena13,
    text="Editar perfil",
    style="EditarPerfil.TButton",
    command=abrir_editar_perfil
)
btn_editar_perfil.place(relx=0.75, rely=0.62, anchor="center")

#Fin de escena 13

# =====================================================
# ESCENA 14 — BUSCAR VUELOS
# =====================================================

def buscar_vuelos_usuario():
    origen = origen_var.get().strip()
    destino = destino_var.get().strip()

    if not origen or not destino:
        messagebox.showerror("Error", "Debe seleccionar origen y destino.")
        return

    if origen == destino:
        messagebox.showerror("Error", "El destino no puede ser igual al origen.")
        return

    vuelos = sistema.buscarVuelos(origen, destino)
    mostrar_resultados(vuelos)


def mostrar_resultados(vuelos):
    resultado_vuelos.delete("1.0", tk.END)

    if not vuelos:
        resultado_vuelos.insert(tk.END, "No se encontraron vuelos disponibles.\n")
        return

    for v in vuelos:
        linea = (
            f"ID: {v.getId()} | "
            f"{v.getCiudadOrigen()} → {v.getCiudadDestino()} | "
            f"Fecha: {v.getFecha()} | "
            f"Pref: {v.getSillasPref()} | "
            f"Econ: {v.getSillasEco()}\n"
        )
        resultado_vuelos.insert(tk.END, linea)


def reservar_vuelo_desde_14():
    texto = resultado_vuelos.get("1.0", tk.END).strip()

    if texto == "":
        messagebox.showerror("Error", "Primero busque un vuelo.")
        return

    id_vuelo = simpledialog.askstring("Seleccionar vuelo", "Ingrese el ID del vuelo que desea reservar:")

    if not id_vuelo:
        return

    v = sistema.buscarVuelo(id_vuelo)

    if not v:
        messagebox.showerror("Error", "El vuelo no existe.")
        return

    vuelo_seleccionado.set(id_vuelo)
    cambiar_escena(escena141)


# ----- Construcción de ESCENA 14 -----

escena14 = ttk.Frame(app)
escena14.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_reservar_img = Image.open("opciones_usuario.png")
fondo_reservar_tk = ImageTk.PhotoImage(fondo_reservar_img)
tk.Label(escena14, image=fondo_reservar_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena14.fondo_reservar_tk = fondo_reservar_tk

style.configure("Buscar.TButton", font=("Triforce", 18, "bold"), background="#1E4C7A", foreground="white")
btn_buscar = ttk.Button(escena14, text="Buscar Vuelos", style="Buscar.TButton", command=buscar_vuelos_usuario)
btn_buscar.place(relx=0.5, rely=0.4, anchor="center")

resultado_vuelos = tk.Text(
    escena14, width=80, height=10, font=("Consolas", 12),
    bg="#16304C", fg="white"
)
resultado_vuelos.place(relx=0.5, rely=0.65, anchor="center")

style.configure("Reservar.TButton", font=("Triforce", 18, "bold"), background="#D4AF37", foreground="white")
btn_reservar = ttk.Button(escena14, text="Reservar Vuelo", style="Reservar.TButton",
                          command=reservar_vuelo_desde_14)
btn_reservar.place(relx=0.80, rely=0.88, anchor="center")

style.configure("Volver14.TButton", font=("Triforce", 18, "bold"), background="#8B0000", foreground="white")
btn_volver_14 = ttk.Button(escena14, text="Volver", style="Volver14.TButton",
                           command=lambda: cambiar_escena(escena13))
btn_volver_14.place(relx=0.20, rely=0.88, anchor="center")

CIUDADES = ["ORNI", "ZORA", "GORON", "CASTILLO", "KAKARIKO", "HYLIA"]

origen_var = tk.StringVar()
destino_var = tk.StringVar()
vuelo_seleccionado = tk.StringVar() 
ttk.Label(escena14, text="Ciudad de Origen:", font=("Triforce", 16),
          background="#16304C", foreground="white").place(relx=0.20, rely=0.22, anchor="w")

combo_origen = ttk.Combobox(escena14, textvariable=origen_var, values=CIUDADES, width=25, state="readonly")
combo_origen.place(relx=0.40, rely=0.22, anchor="w")

ttk.Label(escena14, text="Ciudad de Destino:", font=("Triforce", 16),
          background="#16304C", foreground="white").place(relx=0.20, rely=0.30, anchor="w")

combo_destino = ttk.Combobox(escena14, textvariable=destino_var, values=CIUDADES, width=25, state="readonly")
combo_destino.place(relx=0.40, rely=0.30, anchor="w")


# =====================================================
# ESCENA 14.1 — CONFIGURAR RESERVA
# =====================================================

escena141 = ttk.Frame(app)
escena141.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_141_img = Image.open("opciones_usuario.png")
fondo_141_tk = ImageTk.PhotoImage(fondo_141_img)
tk.Label(escena141, image=fondo_141_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena141.fondo_141_tk = fondo_141_tk

ttk.Label(
    escena141, text="CONFIGURAR RESERVA",
    font=("Triforce", 32, "bold"),
    background="#16304C", foreground="white"
).place(relx=0.5, rely=0.12, anchor="center")

# Tipo de silla
ttk.Label(escena141, text="Tipo de Silla:", font=("Triforce", 18),
          background="#16304C", foreground="white").place(relx=0.25, rely=0.25, anchor="e")
tipo_silla_var = tk.StringVar()
ttk.Combobox(escena141, textvariable=tipo_silla_var,
             values=["Preferencial", "Economica"], state="readonly").place(relx=0.27, rely=0.25, anchor="w")

# Cantidad de sillas
ttk.Label(escena141, text="Cantidad:", font=("Triforce", 18),
          background="#16304C", foreground="white").place(relx=0.25, rely=0.33, anchor="e")
cant_sillas_var = tk.IntVar()
ttk.Combobox(escena141, textvariable=cant_sillas_var,
             values=[1, 2, 3], state="readonly").place(relx=0.27, rely=0.33, anchor="w")

# Equipaje
ttk.Label(escena141, text="Equipaje:", font=("Triforce", 18),
          background="#16304C", foreground="white").place(relx=0.25, rely=0.41, anchor="e")

equip_cab_var = tk.IntVar()
equip_bod_var = tk.IntVar()
equip_man_var = tk.IntVar()

ttk.Checkbutton(escena141, text="Cabina (+40k)", variable=equip_cab_var).place(relx=0.29, rely=0.41)
ttk.Checkbutton(escena141, text="Bodega (+90k)", variable=equip_bod_var).place(relx=0.29, rely=0.46)
ttk.Checkbutton(escena141, text="Mano (Gratis)", variable=equip_man_var).place(relx=0.29, rely=0.51)

# Pasajeros
ttk.Label(escena141, text="Pasajeros (Nombre - ID):", font=("Triforce", 18),
          background="#16304C", foreground="white").place(relx=0.25, rely=0.60, anchor="e")

entrada_pasajeros = tk.Text(escena141, width=40, height=4, bg="#16304C", fg="white", font=("Consolas", 12))
entrada_pasajeros.place(relx=0.27, rely=0.68)


style.configure("Confirmar141.TButton", font=("Triforce", 18, "bold"),
                background="#2E8B57", foreground="white")
ttk.Button(escena141, text="Confirmar Reserva",
           style="Confirmar141.TButton",
           command=confirmar_reserva).place(relx=0.70, rely=0.90, anchor="center")

style.configure("Volver141.TButton", font=("Triforce", 18, "bold"),
                background="#8B0000", foreground="white")
ttk.Button(escena141, text="Volver",
           style="Volver141.TButton",
           command=lambda: cambiar_escena(escena14)).place(relx=0.30, rely=0.90, anchor="center")


# =====================================================
# ESCENA 15 — MIS RESERVAS
# =====================================================

escena15 = ttk.Frame(app)
escena15.place(relx=0, rely=0, relwidth=1, relheight=1)

# Fondo
fondo_mis_reservas_img = Image.open("opciones_usuario.png")
fondo_mis_reservas_tk = ImageTk.PhotoImage(fondo_mis_reservas_img)
fondo_label = tk.Label(escena15, image=fondo_mis_reservas_tk)
fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
fondo_label.lower()  # <-- ENVÍA EL FONDO ABAJO DE TODO
# Título
ttk.Label(
    escena15,
    text="MIS RESERVAS",
    font=("Triforce", 32, "bold"),
    background="#16304C",
    foreground="white"
).place(relx=0.5, rely=0.18, anchor="center")

cols = ("codigo", "vuelo", "destino", "dia", "cantidad", "estado")

tabla_reservas_usuario = ttk.Treeview(
    escena15,
    columns=cols,
    show="headings",
    height=10
)

tabla_reservas_usuario.heading("codigo", text="Código")
tabla_reservas_usuario.heading("vuelo", text="Vuelo")
tabla_reservas_usuario.heading("destino", text="Destino")
tabla_reservas_usuario.heading("dia", text="Día / Fecha")
tabla_reservas_usuario.heading("cantidad", text="Cantidad")
tabla_reservas_usuario.heading("estado", text="Estado")


tabla_reservas_usuario.column("codigo", width=90, anchor="center")
tabla_reservas_usuario.column("vuelo", width=120, anchor="center")
tabla_reservas_usuario.column("destino", width=150, anchor="center")
tabla_reservas_usuario.column("dia", width=200, anchor="center")
tabla_reservas_usuario.column("cantidad", width=90, anchor="center")
tabla_reservas_usuario.column("estado", width=120, anchor="center")


tabla_reservas_usuario.place(relx=0.5, rely=0.52, anchor="center", width=950, height=260)

scroll_y_usuario = ttk.Scrollbar(
    escena15, orient="vertical",
    command=tabla_reservas_usuario.yview
)
scroll_y_usuario.place(relx=0.965, rely=0.52, anchor="center", height=260)

tabla_reservas_usuario.configure(yscrollcommand=scroll_y_usuario.set)

def seleccionar_reserva():
    sel = tabla_reservas_usuario.selection()
    if not sel:
        messagebox.showerror("Error", "Debe seleccionar una reserva.")
        return False

    item = tabla_reservas_usuario.item(sel[0])
    valores = item["values"]
    reserva_seleccionada.set(valores[0])  
    return True
# ============================
# BOTONES
# ============================

style.configure("Volver15.TButton", font=("Triforce", 18, "bold"),
                background="#8B0000", foreground="white")
ttk.Button(
    escena15, text="Volver", style="Volver15.TButton",
    command=lambda: cambiar_escena(escena13)
).place(relx=0.20, rely=0.90, anchor="center")

style.configure("CheckIn15.TButton", font=("Triforce", 18, "bold"),
                background="#2E8B57", foreground="white")
ttk.Button(
    escena15, text="Check-In", style="CheckIn15.TButton",
    command=lambda: abrir_checkin_usuario()

).place(relx=0.40, rely=0.90, anchor="center")

style.configure("Modificar15.TButton", font=("Triforce", 18, "bold"),
                background="#D4AF37", foreground="white")
ttk.Button(
    escena15, text="Modificar", style="Modificar15.TButton",
    command=lambda: seleccionar_reserva_para_modificar()
).place(relx=0.60, rely=0.90, anchor="center")

style.configure("Cancelar15.TButton", font=("Triforce", 18, "bold"),
                background="#8B0000", foreground="white")
ttk.Button(
    escena15, text="Cancelar Reserva", style="Cancelar15.TButton",
    command=lambda: abrir_cancelacion_usuario()
).place(relx=0.80, rely=0.90, anchor="center")

for widget in escena15.winfo_children():
    if isinstance(widget, ttk.Button) or isinstance(widget, ttk.Label):
        widget.lift()
print("Ordenando capas de escena15...")
for w in escena15.winfo_children():
    print(w)
# ================================
# ESCENA 16 - CHECK-IN
# ================================
escena16 = ttk.Frame(app)
escena16.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_checkin_tk = Image.open("opciones_usuario.png")
fondo_checkin_tk = ImageTk.PhotoImage(fondo_checkin_tk)
tk.Label(escena16, image=fondo_checkin_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena16.fondo_checkin_tk = fondo_checkin_tk

titulo_check = ttk.Label(
    escena16,
    text="CHECK-IN DEL VUELO",
    font=("Triforce", 32, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_check.place(relx=0.5, rely=0.10, anchor="center")

datos_reserva = ttk.Label(
    escena16,
    text="Vuelo: —   |   Día: —   |   Sillas: —",
    font=("Triforce", 18),
    background="#16304C",
    foreground="white"
)
datos_reserva.place(relx=0.5, rely=0.20, anchor="center")
lbl_mano = ttk.Label(
    escena16,
    text="Equipaje de Mano:",
    font=("Triforce", 16),
    background="#16304C",
    foreground="white"
)
lbl_mano.place(relx=0.25, rely=0.33, anchor="w")

mano_var = tk.IntVar(value=0)
spin_mano = ttk.Spinbox(
    escena16,
    from_=0, to=2,
    textvariable=mano_var,
    width=5
)
spin_mano.place(relx=0.45, rely=0.33, anchor="w")

lbl_cabina = ttk.Label(
    escena16,
    text="Equipaje Cabina:",
    font=("Triforce", 16),
    background="#16304C",
    foreground="white"
)
lbl_cabina.place(relx=0.25, rely=0.41, anchor="w")

cabina_var = tk.IntVar(value=0)
spin_cabina = ttk.Spinbox(
    escena16,
    from_=0, to=3,
    textvariable=cabina_var,
    width=5
)
spin_cabina.place(relx=0.45, rely=0.41, anchor="w")

style.configure(
    "ConfirmarCheck.TButton",
    font=("Triforce", 18, "bold"),
    background="#2E8B57",
    foreground="white"
)

btn_confirmar_checkin = ttk.Button(
    escena16,
    text="Confirmar Check-in",
    style="ConfirmarCheck.TButton",
    command=lambda: confirmar_checkin()
)
btn_confirmar_checkin.place(relx=0.70, rely=0.70, anchor="center")

lbl_bodega = ttk.Label(
    escena16,
    text="Equipaje Bodega:",
    font=("Triforce", 16),
    background="#16304C",
    foreground="white"
)
lbl_bodega.place(relx=0.25, rely=0.49, anchor="w")

bodega_var = tk.IntVar(value=0)
spin_bodega = ttk.Spinbox(
    escena16,
    from_=0, to=4,
    textvariable=bodega_var,
    width=5
)
spin_bodega.place(relx=0.45, rely=0.49, anchor="w")

style.configure(
    "VolverCheck.TButton",
    font=("Triforce", 18, "bold"),
    background="#8B0000",
    foreground="white"
)

btn_volver_check = ttk.Button(
    escena16,
    text="Volver",
    style="VolverCheck.TButton",
    command=lambda: cambiar_escena(escena15)
)
btn_volver_check.place(relx=0.30, rely=0.70, anchor="center")

# ================================
# ESCENA 17 - MODIFICAR RESERVA
# ================================
escena17 = ttk.Frame(app)
escena17.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_mod_img = Image.open("opciones_usuario.png")
fondo_mod_tk = ImageTk.PhotoImage(fondo_mod_img)
tk.Label(escena17, image=fondo_mod_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena17.fondo_mod_tk = fondo_mod_tk

titulo_mod = ttk.Label(
    escena17,
    text="MODIFICAR RESERVA",
    font=("Triforce", 32, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_mod.place(relx=0.5, rely=0.08, anchor="center")

datos_mod = ttk.Label(
    escena17,
    text="Vuelo: —   |   Día actual: —   |   Sillas: —",
    font=("Triforce", 18),
    background="#16304C",
    foreground="white"
)
datos_mod.place(relx=0.5, rely=0.18, anchor="center")

lbl_sillas_mod = ttk.Label(
    escena17,
    text="Nueva cantidad de sillas:",
    font=("Triforce", 16),
    background="#16304C",
    foreground="white"
)
lbl_sillas_mod.place(relx=0.25, rely=0.33, anchor="w")

sillas_mod_var = tk.IntVar(value=1)
spin_sillas_mod = ttk.Spinbox(
    escena17,
    from_=1, to=10,
    width=5,
    textvariable=sillas_mod_var
)
spin_sillas_mod.place(relx=0.50, rely=0.33, anchor="w")

lbl_dia_mod = ttk.Label(
    escena17,
    text="Nuevo día del vuelo:",
    font=("Triforce", 16),
    background="#16304C",
    foreground="white"
)
lbl_dia_mod.place(relx=0.25, rely=0.42, anchor="w")

dias_semana = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]

dia_mod_var = tk.StringVar()
combo_dia_mod = ttk.Combobox(
    escena17,
    textvariable=dia_mod_var,
    values=dias_semana,
    state="readonly",
    width=20
)
combo_dia_mod.place(relx=0.50, rely=0.42, anchor="w")

lbl_tipo_asiento = ttk.Label(
    escena17,
    text="Tipo de asiento:",
    font=("Triforce", 16),
    background="#16304C",
    foreground="white"
)
lbl_tipo_asiento.place(relx=0.25, rely=0.51, anchor="w")

tipo_asiento_var = tk.StringVar()
combo_tipo_asiento = ttk.Combobox(
    escena17,
    textvariable=tipo_asiento_var,
    values=["Preferencial", "Económico"],
    state="readonly",
    width=20
)
combo_tipo_asiento.place(relx=0.50, rely=0.51, anchor="w")
lbl_pasajeros_mod = ttk.Label(
    escena17,
    text="Pasajeros (Nombre - Documento):",
    font=("Triforce", 16),
    background="#16304C",
    foreground="white"
)
lbl_pasajeros_mod.place(relx=0.25, rely=0.60, anchor="w")

entrada_pasajeros_mod = tk.Text(
    escena17,
    width=40,
    height=5,
    bg="#16304C",
    fg="white",
    font=("Consolas", 12)
)
entrada_pasajeros_mod.place(relx=0.50, rely=0.75, anchor="center")
style.configure("Volver17.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

btn_volver17 = ttk.Button(
    escena17,
    text="Volver",
    style="Volver17.TButton",
    command=lambda: cambiar_escena(escena15)
)
btn_volver17.place(relx=0.30, rely=0.89, anchor="center")

style.configure("Aplicar17.TButton",
                font=("Triforce", 18, "bold"),
                background="#D4AF37",
                foreground="white")

btn_aplicar17 = ttk.Button(
    escena17,
    text="Aplicar cambios",
    style="Aplicar17.TButton",
    command=lambda: aplicar_cambios_reserva()
)
btn_aplicar17.place(relx=0.70, rely=0.89, anchor="center")

# =====================================================
# ESCENA 18 — CANCELAR RESERVA
# =====================================================

escena18 = ttk.Frame(app)
escena18.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_cancel_img = Image.open("opciones_usuario.png")
fondo_cancel_tk = ImageTk.PhotoImage(fondo_cancel_img)
tk.Label(escena18, image=fondo_cancel_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena18.fondo_cancel_tk = fondo_cancel_tk

titulo_cancel = ttk.Label(
    escena18,
    text="CANCELAR RESERVA",
    font=("Triforce", 32, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_cancel.place(relx=0.5, rely=0.08, anchor="center")

datos_cancel = ttk.Label(
    escena18,
    text="Vuelo: —   |   Día: —   |   Sillas: —",
    font=("Triforce", 18),
    background="#16304C",
    foreground="white"
)
datos_cancel.place(relx=0.5, rely=0.18, anchor="center")

msg_advertencia = ttk.Label(
    escena18,
    text="⚠ ¿Está seguro de que desea cancelar esta reserva?\nEsta acción no se puede deshacer.",
    font=("Triforce", 20),
    background="#8B0000",
    foreground="white",
    justify="center",
    padding=10
)
msg_advertencia.place(relx=0.5, rely=0.40, anchor="center")

style.configure(
    "Volver18.TButton",
    font=("Triforce", 18, "bold"),
    background="#1E4C7A",
    foreground="white"
)

btn_volver18 = ttk.Button(
    escena18,
    text="Volver",
    style="Volver18.TButton",
    command=lambda: cambiar_escena(escena15)
)
btn_volver18.place(relx=0.30, rely=0.75, anchor="center")

style.configure(
    "Cancelar18.TButton",
    font=("Triforce", 18, "bold"),
    background="#B22222",
    foreground="white"
)

btn_cancelar18 = ttk.Button(
    escena18,
    text="Cancelar Reserva",
    style="Cancelar18.TButton",
    command=cancelar_reserva
)
btn_cancelar18.place(relx=0.70, rely=0.75, anchor="center")


# ================================
# ESCENA 19 - MILLAS DEL USUARIO
# ================================
def abrir_mis_millas():
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesión.")
        return

    millas_var.set(f"Millas acumuladas: {usuario_actual.getMillas()}")

    cambiar_escena(escena19)


escena19 = ttk.Frame(app)
escena19.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_millas_img = Image.open("opciones_usuario.png")
fondo_millas_tk = ImageTk.PhotoImage(fondo_millas_img)
tk.Label(escena19, image=fondo_millas_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena19.fondo_millas_tk = fondo_millas_tk
titulo_millas = ttk.Label(
    escena19,
    text="MIS MILLAS",
    font=("Triforce", 32, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_millas.place(relx=0.5, rely=0.08, anchor="center")
millas_var = tk.StringVar(value="—")

millas_usuario = ttk.Label(
    escena19,
    textvariable=millas_var,
    font=("Triforce", 22),
    background="#16304C",
    foreground="white"
)

millas_usuario.place(relx=0.5, rely=0.20, anchor="center")
beneficios = ttk.Label(
    escena19,
    text=(
        "Beneficios disponibles:\n\n"
        "• 5% de descuento — 5,000 millas\n"
        "• Upgrade a Preferencial — 8,000 millas\n"
        "• Equipaje extra — 12,000 millas\n"
        "• Viaje gratis — 20,000 millas\n"
    ),
    font=("Triforce", 18),
    background="#16304C",
    foreground="white",
    justify="left"
)
beneficios.place(relx=0.5, rely=0.45, anchor="center")
style.configure(
    "VolverMillas.TButton",
    font=("Triforce", 18, "bold"),
    background="#8B0000",
    foreground="white"
)

btn_volver_millas = ttk.Button(
    escena19,
    text="Volver",
    style="VolverMillas.TButton",
    command=lambda: cambiar_escena(escena13)
)
btn_volver_millas.place(relx=0.5, rely=0.85, anchor="center")

# ================================
# ESCENA 20 - MODIFICAR USUARIO
# ================================


def guardar_cambios_usuario():
    if not usuario_actual:
        messagebox.showerror("Error", "No hay usuario cargado.")
        return

    nuevo_nombre = usr_nombre_var.get().strip()
    nuevo_correo = usr_correo_var.get().strip()
    nueva_pass = usr_pass_var.get().strip()

    if nuevo_nombre == "" or nuevo_correo == "" or nueva_pass == "":
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    usuario_actual.setNombre(nuevo_nombre)
    usuario_actual.setEmail(nuevo_correo)
    usuario_actual.setContrasena(nueva_pass)

    sistema.guardarInfo()

    messagebox.showinfo("Éxito", "Datos actualizados correctamente.")
    cambiar_escena(escena13)


escena20 = ttk.Frame(app)
escena20.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_modusr_img = Image.open("opciones_usuario.png")
fondo_modusr_tk = ImageTk.PhotoImage(fondo_modusr_img)
tk.Label(escena20, image=fondo_modusr_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena20.fondo_modusr_tk = fondo_modusr_tk
titulo_modusr = ttk.Label(
    escena20,
    text="MODIFICAR USUARIO",
    font=("Triforce", 32, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_modusr.place(relx=0.5, rely=0.08, anchor="center")
usr_doc_var = tk.StringVar(value="—")
usr_nombre_var = tk.StringVar(value="—")
usr_correo_var = tk.StringVar(value="—")
usr_tel_var = tk.StringVar(value="—")
usr_pass_var = tk.StringVar(value="—")
lbl_doc = ttk.Label(escena20, text="Documento:", font=("Triforce", 18),
                    background="#16304C", foreground="white")
lbl_doc.place(relx=0.25, rely=0.22, anchor="w")

entry_doc = ttk.Entry(escena20, textvariable=usr_doc_var, width=30, state="disabled")
entry_doc.place(relx=0.45, rely=0.22, anchor="w")
lbl_nom = ttk.Label(escena20, text="Nombre:", font=("Triforce", 18),
                    background="#16304C", foreground="white")
lbl_nom.place(relx=0.25, rely=0.30, anchor="w")

entry_nom = ttk.Entry(escena20, textvariable=usr_nombre_var, width=30)
entry_nom.place(relx=0.45, rely=0.30, anchor="w")
lbl_correo = ttk.Label(escena20, text="Correo:", font=("Triforce", 18),
                       background="#16304C", foreground="white")
lbl_correo.place(relx=0.25, rely=0.38, anchor="w")

entry_correo = ttk.Entry(escena20, textvariable=usr_correo_var, width=30)
entry_correo.place(relx=0.45, rely=0.38, anchor="w")

lbl_pass = ttk.Label(escena20, text="Contraseña:", font=("Triforce", 18),
                     background="#16304C", foreground="white")
lbl_pass.place(relx=0.25, rely=0.54, anchor="w")

entry_pass = ttk.Entry(escena20, textvariable=usr_pass_var, width=30, show="*")
entry_pass.place(relx=0.45, rely=0.54, anchor="w")
style.configure("Volver20.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

btn_volver20 = ttk.Button(
    escena20,
    text="Volver",
    style="Volver20.TButton",
    command=lambda: cambiar_escena(escena13)
)
btn_volver20.place(relx=0.30, rely=0.75, anchor="center")
style.configure("Guardar20.TButton",
                font=("Triforce", 18, "bold"),
                background="#D4AF37",
                foreground="white")

btn_guardar20 = ttk.Button(
    escena20,
    text="Guardar cambios",
    style="Guardar20.TButton",
    command=guardar_cambios_usuario
)
btn_guardar20.place(relx=0.70, rely=0.75, anchor="center")

#================================
# ESCENA 11 - REGISTRO USUARIO
#================================
escena11 = ttk.Frame(app)
escena11.place(relx=0, rely=0, relwidth=1, relheight=1)
fondo_reg_img = Image.open("Inicio.jpg")
fondo_reg_tk = ImageTk.PhotoImage(fondo_reg_img)
tk.Label(escena11, image=fondo_reg_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena11.fondo_reg_tk = fondo_reg_tk

titulo_reg = ttk.Label(
    escena11,
    text="REGISTRO DE USUARIO",
    font=("Triforce", 32, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_reg.place(relx=0.5, rely=0.08, anchor="center")

reg_doc_var = tk.StringVar()
reg_nombre_var = tk.StringVar()
reg_correo_var = tk.StringVar()
reg_tel_var = tk.StringVar()
reg_pass_var = tk.StringVar()
reg_pass2_var = tk.StringVar()

lbl_doc_r = ttk.Label(escena11, text="Documento:",
                      font=("Triforce", 18), background="#16304C", foreground="white")
lbl_doc_r.place(relx=0.25, rely=0.20, anchor="w")

entry_doc_r = ttk.Entry(escena11, textvariable=reg_doc_var, width=35)
entry_doc_r.place(relx=0.47, rely=0.20, anchor="w")

lbl_nom_r = ttk.Label(escena11, text="Nombre completo:",
                      font=("Triforce", 18), background="#16304C", foreground="white")
lbl_nom_r.place(relx=0.25, rely=0.28, anchor="w")

entry_nom_r = ttk.Entry(escena11, textvariable=reg_nombre_var, width=35)
entry_nom_r.place(relx=0.47, rely=0.28, anchor="w")

lbl_cor_r = ttk.Label(escena11, text="Correo electrónico:",
                      font=("Triforce", 18), background="#16304C", foreground="white")
lbl_cor_r.place(relx=0.25, rely=0.36, anchor="w")

entry_cor_r = ttk.Entry(escena11, textvariable=reg_correo_var, width=35)
entry_cor_r.place(relx=0.47, rely=0.36, anchor="w")

lbl_tel_r = ttk.Label(escena11, text="Teléfono:",
                      font=("Triforce", 18), background="#16304C", foreground="white")
lbl_tel_r.place(relx=0.25, rely=0.44, anchor="w")

entry_tel_r = ttk.Entry(escena11, textvariable=reg_tel_var, width=35)
entry_tel_r.place(relx=0.47, rely=0.44, anchor="w")

lbl_pass_r = ttk.Label(escena11, text="Contraseña:",
                       font=("Triforce", 18), background="#16304C", foreground="white")
lbl_pass_r.place(relx=0.25, rely=0.52, anchor="w")

entry_pass_r = ttk.Entry(escena11, textvariable=reg_pass_var, show="*", width=35)
entry_pass_r.place(relx=0.47, rely=0.52, anchor="w")

lbl_pass2_r = ttk.Label(escena11, text="Repetir contraseña:",
                        font=("Triforce", 18), background="#16304C", foreground="white")
lbl_pass2_r.place(relx=0.25, rely=0.60, anchor="w")

entry_pass2_r = ttk.Entry(escena11, textvariable=reg_pass2_var, show="*", width=35)
entry_pass2_r.place(relx=0.47, rely=0.60, anchor="w")

style.configure("VolverReg.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

registro_msg = ttk.Label(
    escena11,
    text="",
    font=("Triforce", 16),
    background="#16304C",
    foreground="red"
)

registro_msg.place(relx=0.5, rely=0.70, anchor="center")

btn_volver_reg = ttk.Button(
    escena11,
    text="Volver",
    style="VolverReg.TButton",
    command=lambda: (cambiar_escena(escena1))
)
btn_volver_reg.place(relx=0.30, rely=0.80, anchor="center")

style.configure("Registrar.TButton",
                font=("Triforce", 18, "bold"),
                background="#D4AF37",
                foreground="white")

def registrar_usuario():

    nombre = reg_nombre_var.get().strip()
    correo = reg_correo_var.get().strip()
    documento = reg_doc_var.get().strip()
    telefono = reg_tel_var.get().strip()
    contrasena = reg_pass_var.get()
    contrasena2 = reg_pass2_var.get()

    if not nombre or not correo or not documento or not contrasena or not contrasena2:
        registro_msg.config(text="Todos los campos son obligatorios")
        return

    if not documento.isdigit():
        registro_msg.config(text="El documento debe ser un número")
        return

    if contrasena != contrasena2:
        registro_msg.config(text="Las contraseñas no coinciden")
        return

    documento = int(documento)

    nuevo = Usuario(nombre, correo, documento, contrasena)

    if sistema.agregarUsuario(nuevo):
        sistema.guardarInfo()
        registro_msg.config(text="Usuario registrado correctamente", foreground="green")

        reg_nombre_var.set("")
        reg_correo_var.set("")
        reg_doc_var.set("")
        reg_tel_var.set("")
        reg_pass_var.set("")
        reg_pass2_var.set("")

        cambiar_escena(escena1)
    else:
        registro_msg.config(text="Ya existe un usuario con ese documento", foreground="red")

btn_registrar = ttk.Button(
    escena11,
    text="Registrarse",
    style="Registrar.TButton",
    command=registrar_usuario
)
btn_registrar.place(relx=0.70, rely=0.80, anchor="center")


#=============================
# ESCENA 21 - LOGIN ADMIN
#=============================
escena21 = ttk.Frame(app)
escena21.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_admin_img = Image.open("admin.jpg").resize((1200, 850))
fondo_admin_tk = ImageTk.PhotoImage(fondo_admin_img)
tk.Label(escena21, image=fondo_admin_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena21.fondo_admin_tk = fondo_admin_tk

titulo_admin = ttk.Label(
    escena21,
    text="LOGIN ADMINISTRADOR",
    font=("Triforce", 32, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_admin.place(relx=0.5, rely=0.15, anchor="center")

doc_admin_var = tk.StringVar()
pass_admin_var = tk.StringVar()

label_doc = ttk.Label(escena21, text="Usuario:", font=("Triforce", 14), foreground="white", background="#16304C")
label_doc.place(relx=0.38, rely=0.40, anchor="e")
entry_doc = ttk.Entry(escena21, textvariable=doc_admin_var, width=30)
entry_doc.place(relx=0.40, rely=0.40, anchor="w")

label_pass = ttk.Label(escena21, text="Contraseña:", font=("Triforce", 14), foreground="white", background="#16304C")
label_pass.place(relx=0.38, rely=0.48, anchor="e")
entry_pass = ttk.Entry(escena21, textvariable=pass_admin_var, width=30, show="*")
entry_pass.place(relx=0.40, rely=0.48, anchor="w")

login_msg = tk.Label(escena21, text="", font=("Triforce", 12), fg="red", bg="#16304C")
login_msg.place(relx=0.5, rely=0.64, anchor="center")


style.configure(
    "IngresarAdmin.TButton",
    font=("Triforce", 18, "bold"),
    background="#1E4C7A",
    foreground="white"
)

btn_admin_ingresar = ttk.Button(
    escena21,
    text="Ingresar",
    style="IngresarAdmin.TButton",
    command=lambda: intentar_login_Admin()
)
btn_admin_ingresar.place(relx=0.5, rely=0.58, anchor="center")

style.configure(
    "VolverAdmin.TButton",
    font=("Triforce", 16, "bold"),
    background="#8B0000",
    foreground="white"
)

btn_admin_volver = ttk.Button(
    escena21,
    text="Volver",
    style="VolverAdmin.TButton",
    command=lambda: cambiar_escena(escena1)
)
btn_admin_volver.place(relx=0.5, rely=0.70, anchor="center")

# ================================
# ESCENA 22 - PANEL ADMINISTRADOR
# ================================
escena22 = ttk.Frame(app)
escena22.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_adminmenu_img = Image.open("panel_admin.jpg")
fondo_adminmenu_tk = ImageTk.PhotoImage(fondo_adminmenu_img)
tk.Label(escena22, image=fondo_adminmenu_tk).place(relx=0, rely=0, relwidth=1, relheight=1)
escena22.fondo_adminmenu_tk = fondo_adminmenu_tk

titulo_admin_menu = ttk.Label(
    escena22,
    text="PANEL DEL ADMINISTRADOR",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
style.configure("AdminUsuarios.TButton",
                font=("Triforce", 20, "bold"),
                background="#1E4C7A",
                foreground="white")
btn_admin_usuarios = ttk.Button(
    escena22,
    text="Gestionar Usuarios",
    style="AdminUsuarios.TButton",
    command=lambda: cambiar_escena(escena23)
)
btn_admin_usuarios.place(relx=0.5, rely=0.28, anchor="center")

style.configure("AdminVuelos.TButton",
                font=("Triforce", 20, "bold"),
                background="#D4AF37",
                foreground="black")
btn_admin_vuelos = ttk.Button(
    escena22,
    text="Gestionar Vuelos",
    style="AdminVuelos.TButton",
    command=lambda: cambiar_escena(escena28)
)
btn_admin_vuelos.place(relx=0.5, rely=0.38, anchor="center")

style.configure("AdminReservas.TButton",
                font=("Triforce", 20, "bold"),
                background="#2E8B57",
                foreground="white")
btn_admin_reservas = ttk.Button(
    escena22,
    text="Ver Reservas",
    style="AdminReservas.TButton",
    command=lambda: ir_a_escena33()
)
btn_admin_reservas.place(relx=0.5, rely=0.48, anchor="center")

style.configure("AdminStats.TButton",
                font=("Triforce", 20, "bold"),
                background="#4ED3F1",
                foreground="black")
btn_admin_stats = ttk.Button(
    escena22,
    text="Estadísticas",
    style="AdminStats.TButton",
    command=lambda: (actualizar_estadisticas(), cambiar_escena(escena34))
)
btn_admin_stats.place(relx=0.5, rely=0.58, anchor="center")

style.configure("AdminSalir.TButton",
                font=("Triforce", 20, "bold"),
                background="#8B0000",
                foreground="white")
btn_admin_salir = ttk.Button(
    escena22,
    text="Cerrar Sesión",
    style="AdminSalir.TButton",
    command=lambda: (cambiar_escena(escena1), reproducir_musica("musica_incio.mp3"))
)
btn_admin_salir.place(relx=0.5, rely=0.70, anchor="center")

# ================================
# ESCENA 23 - GESTIONAR USUARIOS
# ================================
escena23 = ttk.Frame(app)
escena23.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_gestusr_img = Image.open("opciones_admin.jpg")
fondo_gestusr_tk = ImageTk.PhotoImage(fondo_gestusr_img)
tk.Label(escena23, image=fondo_gestusr_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena23.fondo_gestusr_tk = fondo_gestusr_tk
titulo_gestusr = ttk.Label(
    escena23,
    text="GESTIÓN DE USUARIOS",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_gestusr.place(relx=0.5, rely=0.12, anchor="center")

style.configure("AdminAdd.TButton",
                font=("Triforce", 20, "bold"),
                background="#2E8B57",  
                foreground="white")
btn_add_user = ttk.Button(
    escena23,
    text="Agregar Usuario",
    style="AdminAdd.TButton",
    command=lambda: cambiar_escena(escena24)
)
btn_add_user.place(relx=0.5, rely=0.30, anchor="center")

style.configure("AdminEdit.TButton",
                font=("Triforce", 20, "bold"),
                background="#1E4C7A", 
                foreground="white")
btn_edit_user = ttk.Button(
    escena23,
    text="Editar Usuario",
    style="AdminEdit.TButton",
    command=lambda: cambiar_escena(escena25)
)
btn_edit_user.place(relx=0.5, rely=0.40, anchor="center")

style.configure("AdminDelete.TButton",
                font=("Triforce", 20, "bold"),
                background="#8B0000",   
                foreground="white")
btn_del_user = ttk.Button(
    escena23,
    text="Eliminar Usuario",
    style="AdminDelete.TButton",
    command=lambda: cambiar_escena(escena26)
)
btn_del_user.place(relx=0.5, rely=0.50, anchor="center")

style.configure("AdminView.TButton",
                font=("Triforce", 20, "bold"),
                background="#D4AF37", 
                foreground="black")
btn_view_user = ttk.Button(
    escena23,
    text="Ver Usuarios",
    style="AdminView.TButton",
    command=lambda: cambiar_escena(escena27)
)
btn_view_user.place(relx=0.5, rely=0.60, anchor="center")

style.configure("AdminBack.TButton",
                font=("Triforce", 18, "bold"),
                background="#4C7A46",   
                foreground="white")
btn_back_user = ttk.Button(
    escena23,
    text="Volver",
    style="AdminBack.TButton",
    command=lambda: cambiar_escena(escena22)
)
btn_back_user.place(relx=0.5, rely=0.75, anchor="center")

# ================================
# ESCENA 24 - AGREGAR USUARIO
# ================================
def admin_agregar_usuario():
    nombre = add_nombre_var.get().strip()
    correo = add_correo_var.get().strip()
    documento = add_doc_var.get().strip()
    telefono = add_tel_var.get().strip()
    contrasena = add_pass_var.get()
    contrasena2 = add_pass2_var.get()

    if not nombre or not correo or not documento or not contrasena or not contrasena2:
        add_msg.config(text="Todos los campos son obligatorios", foreground="red")
        return

    if not documento.isdigit():
        add_msg.config(text="El documento debe ser numérico", foreground="red")
        return

    if contrasena != contrasena2:
        add_msg.config(text="Las contraseñas no coinciden", foreground="red")
        return

    documento = int(documento)

    nuevo = Usuario(nombre, correo, documento, contrasena)

    if sistema.agregarUsuario(nuevo):
        add_msg.config(text="Usuario agregado correctamente", foreground="lightgreen")

        sistema.guardarInfo()

        add_nombre_var.set("")
        add_correo_var.set("")
        add_doc_var.set("")
        add_tel_var.set("")
        add_pass_var.set("")
        add_pass2_var.set("")
    else:
        add_msg.config(text="Ya existe un usuario con ese documento", foreground="red")

escena24 = ttk.Frame(app)
escena24.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_addusr_img = Image.open("opciones_admin.jpg")
fondo_addusr_tk = ImageTk.PhotoImage(fondo_addusr_img)
tk.Label(escena24, image=fondo_addusr_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena24.fondo_addusr_tk = fondo_addusr_tk

titulo_addusr = ttk.Label(
    escena24,
    text="AGREGAR USUARIO",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_addusr.place(relx=0.5, rely=0.10, anchor="center")


add_doc_var = tk.StringVar()
add_nombre_var = tk.StringVar()
add_correo_var = tk.StringVar()
add_tel_var = tk.StringVar()
add_pass_var = tk.StringVar()
add_pass2_var = tk.StringVar()

lbl_add_doc = ttk.Label(
    escena24, text="Documento:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_add_doc.place(relx=0.25, rely=0.22, anchor="w")

entry_add_doc = ttk.Entry(
    escena24, textvariable=add_doc_var, width=35
)
entry_add_doc.place(relx=0.47, rely=0.22, anchor="w")

lbl_add_nom = ttk.Label(
    escena24, text="Nombre completo:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_add_nom.place(relx=0.25, rely=0.30, anchor="w")

entry_add_nom = ttk.Entry(
    escena24, textvariable=add_nombre_var, width=35
)
entry_add_nom.place(relx=0.47, rely=0.30, anchor="w")

lbl_add_cor = ttk.Label(
    escena24, text="Correo:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_add_cor.place(relx=0.25, rely=0.38, anchor="w")

entry_add_cor = ttk.Entry(
    escena24, textvariable=add_correo_var, width=35
)
entry_add_cor.place(relx=0.47, rely=0.38, anchor="w")

lbl_add_tel = ttk.Label(
    escena24, text="Teléfono:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_add_tel.place(relx=0.25, rely=0.46, anchor="w")

entry_add_tel = ttk.Entry(
    escena24, textvariable=add_tel_var, width=35
)
entry_add_tel.place(relx=0.47, rely=0.46, anchor="w")

lbl_add_pass = ttk.Label(
    escena24, text="Contraseña:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_add_pass.place(relx=0.25, rely=0.54, anchor="w")

entry_add_pass = ttk.Entry(
    escena24, textvariable=add_pass_var, width=35, show="*"
)
entry_add_pass.place(relx=0.47, rely=0.54, anchor="w")

lbl_add_pass2 = ttk.Label(
    escena24, text="Confirmar contraseña:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_add_pass2.place(relx=0.25, rely=0.62, anchor="w")

entry_add_pass2 = ttk.Entry(
    escena24, textvariable=add_pass2_var, width=35, show="*"
)
entry_add_pass2.place(relx=0.47, rely=0.62, anchor="w")

style.configure("VolverAdd.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

btn_add_volver = ttk.Button(
    escena24,
    text="Volver",
    style="VolverAdd.TButton",
    command=lambda: cambiar_escena(escena23)
)
btn_add_volver.place(relx=0.30, rely=0.75, anchor="center")
add_msg = ttk.Label(
    escena24,
    text="",
    font=("Triforce", 16),
    background="#16304C",
    foreground="yellow"
)
add_msg.place(relx=0.5, rely=0.69, anchor="center")

style.configure("AgregarUsr.TButton",
                font=("Triforce", 18, "bold"),
                background="#2E8B57",
                foreground="white")

btn_add_user = ttk.Button(
    escena24,
    text="Agregar Usuario",
    style="AgregarUsr.TButton",
    command=(admin_agregar_usuario)
)
btn_add_user.place(relx=0.70, rely=0.75, anchor="center")

# ================================
# ESCENA 25 - EDITAR USUARIO
# ================================
def admin_buscar_usuario():
    doc = buscar_doc_var.get().strip()

    if not doc.isdigit():
        messagebox.showerror("Error", "El documento debe ser numérico")
        return

    doc = int(doc)

    usuario = sistema.buscarUsuario(doc)

    if usuario is None:
        messagebox.showerror("Error", "No existe un usuario con ese documento")
        return

    edit_doc_var.set(str(usuario.getId()))
    edit_nom_var.set(usuario.getNombre())
    edit_cor_var.set(usuario.getEmail())
    edit_tel_var.set("--------")
    edit_pass_var.set(usuario.getContrasena())

    messagebox.showinfo("Éxito", f"Usuario {usuario.getNombre()} encontrado.")

def admin_guardar_cambios_usuario():
    doc = edit_doc_var.get().strip()

    if doc == "—" or not doc.isdigit():
        messagebox.showerror("Error", "Primero debe buscar un usuario.")
        return

    doc = int(doc)

    usuario = sistema.buscarUsuario(doc)
    if usuario is None:
        messagebox.showerror("Error", "El usuario ya no existe.")
        return

    nuevo_nombre = edit_nom_var.get().strip()
    nuevo_correo = edit_cor_var.get().strip()
    nueva_pass = edit_pass_var.get()

    if not nuevo_nombre or not nuevo_correo or not nueva_pass:
        messagebox.showerror("Error", "No puede dejar campos vacíos.")
        return

    actualizado = Usuario(
        nuevo_nombre,
        nuevo_correo,
        doc,
        nueva_pass
    )
    actualizado.acumularMillas(usuario.getMillas())

    if sistema.editarUsuario(doc, actualizado):
        sistema.guardarInfo()
        messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
    else:
        messagebox.showerror("Error", "No se pudo actualizar el usuario")

escena25 = ttk.Frame(app)
escena25.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_editusr_img = Image.open("opciones_admin.jpg")
fondo_editusr_tk = ImageTk.PhotoImage(fondo_editusr_img)
tk.Label(escena25, image=fondo_editusr_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena25.fondo_editusr_tk = fondo_editusr_tk

titulo_editusr = ttk.Label(
    escena25,
    text="EDITAR USUARIO",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_editusr.place(relx=0.5, rely=0.08, anchor="center")

buscar_doc_var = tk.StringVar()

edit_doc_var = tk.StringVar(value="—")
edit_nom_var = tk.StringVar(value="—")
edit_cor_var = tk.StringVar(value="—")
edit_tel_var = tk.StringVar(value="—")
edit_pass_var = tk.StringVar(value="—")

lbl_buscar_doc = ttk.Label(
    escena25,
    text="Ingrese documento:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_buscar_doc.place(relx=0.20, rely=0.20, anchor="w")

entry_buscar_doc = ttk.Entry(
    escena25, textvariable=buscar_doc_var, width=25
)
entry_buscar_doc.place(relx=0.45, rely=0.20, anchor="w")

style.configure("BuscarUsr.TButton",
                font=("Triforce", 16, "bold"),
                background="#4ED3F1",
                foreground="black")

btn_buscar_usr = ttk.Button(
    escena25,
    text="Buscar",
    style="BuscarUsr.TButton",
    command=admin_buscar_usuario
)
btn_buscar_usr.place(relx=0.75, rely=0.20, anchor="center")

lbl_edit_doc = ttk.Label(
    escena25, text="Documento:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_edit_doc.place(relx=0.25, rely=0.30, anchor="w")

entry_edit_doc = ttk.Entry(
    escena25, textvariable=edit_doc_var, width=35, state="disabled"
)
entry_edit_doc.place(relx=0.47, rely=0.30, anchor="w")

lbl_edit_nom = ttk.Label(
    escena25, text="Nombre completo:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_edit_nom.place(relx=0.25, rely=0.38, anchor="w")

entry_edit_nom = ttk.Entry(
    escena25, textvariable=edit_nom_var, width=35
)
entry_edit_nom.place(relx=0.47, rely=0.38, anchor="w")

lbl_edit_cor = ttk.Label(
    escena25, text="Correo:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_edit_cor.place(relx=0.25, rely=0.46, anchor="w")

entry_edit_cor = ttk.Entry(
    escena25, textvariable=edit_cor_var, width=35
)
entry_edit_cor.place(relx=0.47, rely=0.46, anchor="w")

lbl_edit_tel = ttk.Label(
    escena25, text="Teléfono:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_edit_tel.place(relx=0.25, rely=0.54, anchor="w")

entry_edit_tel = ttk.Entry(
    escena25, textvariable=edit_tel_var, width=35
)
entry_edit_tel.place(relx=0.47, rely=0.54, anchor="w")

lbl_edit_pass = ttk.Label(
    escena25, text="Contraseña:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_edit_pass.place(relx=0.25, rely=0.62, anchor="w")

entry_edit_pass = ttk.Entry(
    escena25, textvariable=edit_pass_var, width=35, show="*"
)
entry_edit_pass.place(relx=0.47, rely=0.62, anchor="w")

style.configure("VolverEdit.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

btn_edit_volver = ttk.Button(
    escena25,
    text="Volver",
    style="VolverEdit.TButton",
    command=lambda: cambiar_escena(escena23)
)
btn_edit_volver.place(relx=0.30, rely=0.80, anchor="center")

style.configure("GuardarEdit.TButton",
                font=("Triforce", 18, "bold"),
                background="#D4AF37",
                foreground="black")

btn_edit_guardar = ttk.Button(
    escena25,
    text="Guardar Cambios",
    style="GuardarEdit.TButton",
    command= admin_guardar_cambios_usuario
)
btn_edit_guardar.place(relx=0.70, rely=0.80, anchor="center")

# ================================
# ESCENA 26 - ELIMINAR USUARIO
# ================================
def buscar_usuario():
    documento = del_buscar_doc_var.get().strip()
    
    if not documento:
        messagebox.showerror("Error", "Por favor, ingrese un documento")
        return
    
    usuarios = []
    try:
        with open("usuarios.txt", "r") as file:
            usuarios = file.readlines()
    except FileNotFoundError:
        messagebox.showerror("Error", "Archivo de usuarios no encontrado.")
        return
    
    encontrado = False
    for usuario in usuarios:
        datos = usuario.strip().split(",")
        if datos[0] == documento:
            del_doc_var.set(datos[0])
            del_nom_var.set(datos[1])
            del_cor_var.set(datos[2])
            del_tel_var.set(datos[3])
            encontrado = True
            break
    
    if not encontrado:
        messagebox.showerror("Error", "Usuario no encontrado.")
    else:
        messagebox.showinfo("Usuario encontrado", "Usuario cargado correctamente.")

def eliminar_usuario():
    documento = del_buscar_doc_var.get().strip()
    
    if not documento:
        messagebox.showerror("Error", "Por favor, ingrese un documento")
        return
    
    usuarios = []
    try:
        with open("usuarios.txt", "r") as file:
            usuarios = file.readlines()
    except FileNotFoundError:
        messagebox.showerror("Error", "Archivo de usuarios no encontrado.")
        return
    
    encontrado = False
    with open("usuarios.txt", "w") as file: 
        for usuario in usuarios:
            datos = usuario.strip().split(",")  
            if datos[0] == documento:  
                encontrado = True
                continue 
            file.write(usuario)

    if not encontrado:
        messagebox.showerror("Error", "Usuario no encontrado.")
    else:
        messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
        # Limpiar campos
        del_doc_var.set("")
        del_nom_var.set("")
        del_cor_var.set("")
        del_tel_var.set("")

escena26 = ttk.Frame(app)
escena26.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_delusr_img = Image.open("opciones_admin.jpg")
fondo_delusr_tk = ImageTk.PhotoImage(fondo_delusr_img)
tk.Label(escena26, image=fondo_delusr_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena26.fondo_delusr_tk = fondo_delusr_tk

titulo_delusr = ttk.Label(
    escena26,
    text="ELIMINAR USUARIO",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_delusr.place(relx=0.5, rely=0.10, anchor="center")

del_buscar_doc_var = tk.StringVar()

del_doc_var = tk.StringVar(value="—")
del_nom_var = tk.StringVar(value="—")
del_cor_var = tk.StringVar(value="—")
del_tel_var = tk.StringVar(value="—")

lbl_del_buscar = ttk.Label(
    escena26,
    text="Ingrese documento:",
    font=("Triforce",18),
    background="#16304C", foreground="white"
)
lbl_del_buscar.place(relx=0.20, rely=0.20, anchor="w")

entry_del_buscar = ttk.Entry(
    escena26, textvariable=del_buscar_doc_var, width=25
)
entry_del_buscar.place(relx=0.45, rely=0.20, anchor="w")

style.configure("BuscarDelUsr.TButton",
                font=("Triforce", 16, "bold"),
                background="#4ED3F1",
                foreground="black")

btn_del_buscar = ttk.Button(
    escena26,
    text="Buscar",
    style="BuscarDelUsr.TButton",
    command= buscar_usuario
)
btn_del_buscar.place(relx=0.75, rely=0.20, anchor="center")

lbl_del_doc = ttk.Label(
    escena26, text="Documento:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_del_doc.place(relx=0.25, rely=0.30, anchor="w")

entry_del_doc = ttk.Entry(
    escena26, textvariable=del_doc_var, width=35, state="disabled"
)
entry_del_doc.place(relx=0.47, rely=0.30, anchor="w")

lbl_del_nom = ttk.Label(
    escena26, text="Nombre:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_del_nom.place(relx=0.25, rely=0.38, anchor="w")

entry_del_nom = ttk.Entry(
    escena26, textvariable=del_nom_var, width=35, state="disabled"
)
entry_del_nom.place(relx=0.47, rely=0.38, anchor="w")

lbl_del_cor = ttk.Label(
    escena26, text="Correo:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_del_cor.place(relx=0.25, rely=0.46, anchor="w")

entry_del_cor = ttk.Entry(
    escena26, textvariable=del_cor_var, width=35, state="disabled"
)
entry_del_cor.place(relx=0.47, rely=0.46, anchor="w")

lbl_del_tel = ttk.Label(
    escena26, text="Teléfono:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_del_tel.place(relx=0.25, rely=0.54, anchor="w")

entry_del_tel = ttk.Entry(
    escena26, textvariable=del_tel_var, width=35, state="disabled"
)
entry_del_tel.place(relx=0.47, rely=0.54, anchor="w")

msg_del_warning = ttk.Label(
    escena26,
    text="⚠ Esta acción no se puede deshacer.",
    font=("Triforce", 20),
    background="#8B0000",
    foreground="white"
)
msg_del_warning.place(relx=0.5, rely=0.65, anchor="center")

style.configure("VolverDelUsr.TButton",
                font=("Triforce", 18, "bold"),
                background="#4C7A46",
                foreground="white")

btn_del_volver = ttk.Button(
    escena26,
    text="Volver",
    style="VolverDelUsr.TButton",
    command=lambda: cambiar_escena(escena23)
)
btn_del_volver.place(relx=0.30, rely=0.80, anchor="center")

style.configure("EliminarUsr.TButton",
                font=("Triforce", 18, "bold"),
                background="#B22222",
                foreground="white")

btn_del_eliminar = ttk.Button(
    escena26,
    text="Eliminar Usuario",
    style="EliminarUsr.TButton",
    command= eliminar_usuario
)
btn_del_eliminar.place(relx=0.70, rely=0.80, anchor="center")

# ================================
# ESCENA 27 - VER USUARIOS
# ================================
def cargar_usuarios():
    tabla_usuarios.delete(*tabla_usuarios.get_children())

    try:
        with open("usuarios.txt", "r") as file:
            for linea in file:
                datos = linea.strip().split(",")
                documento, nombre, correo, _, _ = datos
                tabla_usuarios.insert("", "end", values=(documento, nombre, correo))
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo de usuarios no fue encontrado.")

escena27 = ttk.Frame(app)
escena27.place(relx=0, rely=0, relwidth=1, relheight=1)


fondo_verusr_img = Image.open("opciones_admin.jpg")
fondo_verusr_tk = ImageTk.PhotoImage(fondo_verusr_img)
tk.Label(escena27, image=fondo_verusr_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena27.fondo_verusr_tk = fondo_verusr_tk

titulo_verusr = ttk.Label(
    escena27,
    text="LISTA DE USUARIOS",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_verusr.place(relx=0.5, rely=0.08, anchor="center")

tabla_cols = ("documento", "nombre", "correo")

tabla_usuarios = ttk.Treeview(
    escena27,
    columns=tabla_cols,
    show="headings",
    height=15
)

tabla_usuarios.heading("documento", text="Documento")
tabla_usuarios.heading("nombre", text="Nombre")
tabla_usuarios.heading("correo", text="Correo")


tabla_usuarios.column("documento", width=150, anchor="center")
tabla_usuarios.column("nombre", width=260, anchor="center")
tabla_usuarios.column("correo", width=260, anchor="center")


cargar_usuarios()

tabla_usuarios.place(relx=0.5, rely=0.50, anchor="center")

style.configure("VolverVerUsr.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

btn_verusr_volver = ttk.Button(
    escena27,
    text="Volver",
    style="VolverVerUsr.TButton",
    command=lambda: cambiar_escena(escena23)
)
btn_verusr_volver.place(relx=0.5, rely=0.88, anchor="center")

# ================================
# ESCENA 28 - GESTIONAR VUELOS
# ================================
escena28 = ttk.Frame(app)
escena28.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_gestvuelos_img = Image.open("opciones_admin.jpg")
fondo_gestvuelos_tk = ImageTk.PhotoImage(fondo_gestvuelos_img)
tk.Label(escena28, image=fondo_gestvuelos_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena28.fondo_gestvuelos_tk = fondo_gestvuelos_tk

titulo_gestv = ttk.Label(
    escena28,
    text="GESTIÓN DE VUELOS",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_gestv.place(relx=0.5, rely=0.10, anchor="center")

style.configure("AddFly.TButton",
                font=("Triforce", 20, "bold"),
                background="#2E8B57",
                foreground="white")

style.configure("EditFly.TButton",
                font=("Triforce", 20, "bold"),
                background="#1E4C7A",
                foreground="white")

style.configure("DeleteFly.TButton",
                font=("Triforce", 20, "bold"),
                background="#8B0000",
                foreground="white")

style.configure("ViewFly.TButton",
                font=("Triforce", 20, "bold"),
                background="#D4AF37",
                foreground="black")

style.configure("BackFly.TButton",
                font=("Triforce", 18, "bold"),
                background="#4C7A46",
                foreground="white")

btn_add_fly = ttk.Button(
    escena28,
    text="Agregar Vuelo",
    style="AddFly.TButton",
    command=lambda: cambiar_escena(escena29)
)
btn_add_fly.place(relx=0.5, rely=0.28, anchor="center")

btn_edit_fly = ttk.Button(
    escena28,
    text="Editar Vuelo",
    style="EditFly.TButton",
    command=lambda: cambiar_escena(escena30)
)
btn_edit_fly.place(relx=0.5, rely=0.38, anchor="center")

btn_delete_fly = ttk.Button(
    escena28,
    text="Eliminar Vuelo",
    style="DeleteFly.TButton",
    command=lambda: cambiar_escena(escena31)
)
btn_delete_fly.place(relx=0.5, rely=0.48, anchor="center")

btn_view_fly = ttk.Button(
    escena28,
    text="Ver Vuelos",
    style="ViewFly.TButton",
    command=lambda: ir_a_escena32()
)
btn_view_fly.place(relx=0.5, rely=0.58, anchor="center")

btn_back_fly = ttk.Button(
    escena28,
    text="Volver",
    style="BackFly.TButton",
    command=lambda: cambiar_escena(escena22)
)
btn_back_fly.place(relx=0.5, rely=0.75, anchor="center")

# ================================
# ESCENA 29 - AGREGAR VUELO
# ================================
def validar_fecha(fecha):
    try:
        d, m, a = fecha.split("-")
        d = int(d); m = int(m); a = int(a)
        if 1 <= d <= 31 and 1 <= m <= 12 and a >= 2024:
            return True
        return False
    except:
        return False

def validar_hora(hora):
    try:
        h, mn = hora.split(":")
        h = int(h); mn = int(mn)
        return 0 <= h <= 23 and 0 <= mn <= 59
    except:
        return False


def guardar_vuelo():
    vuelo_code = fly_code_var.get().strip()
    vuelo_origen = fly_origen_var.get().strip()
    vuelo_destino = fly_destino_var.get().strip()
    fecha_str = fly_dia_var.get().strip()
    hora_str = fly_hora_var.get().strip()
    vuelo_pref = fly_pref_var.get()
    vuelo_econ = fly_econ_var.get()

    # ----- Validaciones -----
    if not vuelo_code:
        messagebox.showerror("Error", "Debes ingresar un código de vuelo.")
        return

    if vuelo_origen == "" or vuelo_destino == "":
        messagebox.showerror("Error", "Debes seleccionar origen y destino.")
        return

    if vuelo_origen == vuelo_destino:
        messagebox.showerror("Error", "El origen y destino no pueden ser iguales.")
        return

    if not validar_fecha(fecha_str):
        messagebox.showerror("Error", "La fecha debe tener el formato DD-MM-YYYY.")
        return
    
    if not validar_hora(hora_str):
        messagebox.showerror("Error", "La hora debe tener el formato HH:MM.")
        return

    # ----- Procesar fecha -----
    d, m, a = fecha_str.split("-")
    h, mn = hora_str.split(":")

    try:
        fecha_obj = Fecha(int(d), int(m), int(a), int(h), int(mn))
    except:
        messagebox.showerror("Error", "Fecha u hora inválidas.")
        return

    # ----- Crear objeto Vuelo -----
    try:
        vuelo_obj = Vuelo(
            vuelo_code,
            vuelo_origen,
            vuelo_destino,
            fecha_obj,
            int(vuelo_pref),
            int(vuelo_econ),
            True
        )
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear el vuelo:\n{e}")
        return

    # ----- Guardar en vuelos.txt -----
    try:
        with open("vuelos.txt", "a", encoding="utf-8") as f:
            f.write(f"{vuelo_code},{vuelo_origen},{vuelo_destino},"
                    f"{d}-{m}-{a}-{h}-{mn},{vuelo_pref},{vuelo_econ},True\n")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el vuelo:\n{e}")
        return

    messagebox.showinfo("Éxito", "Vuelo agregado correctamente.")

    fly_code_var.set("")
    fly_origen_var.set("")
    fly_destino_var.set("")
    fly_dia_var.set("")
    fly_hora_var.set("")
    fly_pref_var.set(10)
    fly_econ_var.set(130)

escena29 = ttk.Frame(app)
escena29.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_addfly_img = Image.open("opciones_admin.jpg")
fondo_addfly_tk = ImageTk.PhotoImage(fondo_addfly_img)
tk.Label(escena29, image=fondo_addfly_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena29.fondo_addfly_tk = fondo_addfly_tk
titulo_add_fly = ttk.Label(
    escena29,
    text="AGREGAR VUELO",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_add_fly.place(relx=0.5, rely=0.08, anchor="center")

fly_code_var = tk.StringVar()
fly_origen_var = tk.StringVar()
fly_destino_var = tk.StringVar()
fly_dia_var = tk.StringVar()
fly_hora_var = tk.StringVar()
fly_pref_var = tk.IntVar(value=10)
fly_econ_var = tk.IntVar(value=130)

lbl_fly_code = ttk.Label(
    escena29, text="Código de vuelo:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_fly_code.place(relx=0.23, rely=0.20, anchor="w")

entry_fly_code = ttk.Entry(
    escena29, textvariable=fly_code_var, width=35
)
entry_fly_code.place(relx=0.47, rely=0.20, anchor="w")

lbl_fly_origen = ttk.Label(
    escena29, text="Origen:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_fly_origen.place(relx=0.23, rely=0.28, anchor="w")

combo_fly_origen = ttk.Combobox(
    escena29, textvariable=fly_origen_var,
    values=["ORNI", "ZORA", "GORON", "CASTILLO", "KAKARIKO", "HYLIA"],
    width=30, state="readonly"
)
combo_fly_origen.place(relx=0.47, rely=0.28, anchor="w")

lbl_fly_destino = ttk.Label(
    escena29, text="Destino:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_fly_destino.place(relx=0.23, rely=0.36, anchor="w")

combo_fly_destino = ttk.Combobox(
    escena29, textvariable=fly_destino_var,
    values=["ORNI", "ZORA", "GORON", "CASTILLO", "KAKARIKO", "HYLIA"],
    width=30, state="readonly"
)
combo_fly_destino.place(relx=0.47, rely=0.36, anchor="w")

lbl_fly_fecha = ttk.Label(
    escena29, text="Fecha (DD-MM-YYYY):",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_fly_fecha.place(relx=0.23, rely=0.44, anchor="w")


entry_fly_fecha = ttk.Entry(
    escena29, textvariable=fly_dia_var, width=35
)
entry_fly_fecha.place(relx=0.47, rely=0.44, anchor="w")

lbl_fly_hora = ttk.Label(
    escena29, text="Hora (HH:MM):",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_fly_hora.place(relx=0.23, rely=0.52, anchor="w")

entry_fly_hora = ttk.Entry(
    escena29, textvariable=fly_hora_var, width=35
)
entry_fly_hora.place(relx=0.47, rely=0.52, anchor="w")

lbl_pref = ttk.Label(
    escena29, text="Sillas preferenciales:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_pref.place(relx=0.23, rely=0.60, anchor="w")

entry_pref = ttk.Spinbox(
    escena29, from_=0, to=50, width=10, textvariable=fly_pref_var
)
entry_pref.place(relx=0.47, rely=0.60, anchor="w")

lbl_econ = ttk.Label(
    escena29, text="Sillas económicas:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_econ.place(relx=0.23, rely=0.68, anchor="w")

entry_econ = ttk.Spinbox(
    escena29, from_=0, to=200, width=10, textvariable=fly_econ_var
)
entry_econ.place(relx=0.47, rely=0.68, anchor="w")

style.configure("VolverAddFly.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

btn_addfly_volver = ttk.Button(
    escena29,
    text="Volver",
    style="VolverAddFly.TButton",
    command=lambda: cambiar_escena(escena28)
)
btn_addfly_volver.place(relx=0.30, rely=0.82, anchor="center")

style.configure("AddFlyBtn.TButton",
                font=("Triforce", 18, "bold"),
                background="#2E8B57",
                foreground="white")

btn_addfly = ttk.Button(
    escena29,
    text="Agregar Vuelo",
    style="AddFlyBtn.TButton",
    command=guardar_vuelo
)
btn_addfly.place(relx=0.70, rely=0.82, anchor="center")

# ================================
# ESCENA 30 - EDITAR VUELO
# ================================
def buscar_vuelo_editar():
    codigo = buscar_vuelo_var.get().strip()

    if not codigo:
        messagebox.showerror("Error", "Ingrese un código de vuelo.")
        return

    encontrado = False

    try:
        with open("vuelos.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")

                if datos[0] == codigo:
                    encontrado = True

                    cod, ori, dest = datos[0], datos[1], datos[2]
                    fecha_completa = datos[3]
                    pref, econ = datos[4], datos[5]

                    dd, mm, aa, hh, mn = fecha_completa.split("-")

                    edit_code_var.set(cod)
                    edit_origen_var.set(ori)
                    edit_destino_var.set(dest)
                    edit_dia_var.set(f"{dd}-{mm}-{aa}")
                    edit_hora_var.set(f"{hh}:{mn}")
                    edit_pref_var.set(pref)
                    edit_econ_var.set(econ)

                    break
    except FileNotFoundError:
        messagebox.showerror("Error", "No existe el archivo vuelos.txt.")
        return

    if not encontrado:
        messagebox.showerror("Error", "Vuelo no encontrado.")

def guardar_cambios_vuelo():
    cod = edit_code_var.get()
    ori = edit_origen_var.get()
    dest = edit_destino_var.get()
    fecha_str = edit_dia_var.get()
    hora_str = edit_hora_var.get()
    pref = edit_pref_var.get()
    econ = edit_econ_var.get()

    if cod == "—":
        messagebox.showerror("Error", "No se ha cargado ningún vuelo.")
        return

    if ori == "" or dest == "":
        messagebox.showerror("Error", "Origen y destino no pueden estar vacíos.")
        return

    if ori == dest:
        messagebox.showerror("Error", "Origen y destino no pueden ser iguales.")
        return

    if not validar_fecha(fecha_str):
        messagebox.showerror("Error", "La fecha debe ser DD-MM-YYYY.")
        return

    if not validar_hora(hora_str):
        messagebox.showerror("Error", "La hora debe ser HH:MM.")
        return

    d, m, a = fecha_str.split("-")
    h, mn = hora_str.split(":")

    linea_nueva = f"{cod},{ori},{dest},{d}-{m}-{a}-{h}-{mn},{pref},{econ},True\n"

    nuevas_lineas = []

    try:
        with open("vuelos.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")
                if datos[0] == cod:
                    nuevas_lineas.append(linea_nueva)
                else:
                    nuevas_lineas.append(linea)
    except:
        messagebox.showerror("Error", "No se pudo leer vuelos.txt.")
        return

    try:
        with open("vuelos.txt", "w", encoding="utf-8") as f:
            for l in nuevas_lineas:
                f.write(l)
    except:
        messagebox.showerror("Error", "No se pudo escribir vuelos.txt.")
        return

    messagebox.showinfo("Éxito", "Vuelo actualizado correctamente.")

escena30 = ttk.Frame(app)
escena30.place(relx=0, rely=0, relwidth=1, relheight=1)

# Fondo
fondo_editfly_img = Image.open("opciones_admin.jpg")
fondo_editfly_tk = ImageTk.PhotoImage(fondo_editfly_img)
tk.Label(escena30, image=fondo_editfly_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena30.fondo_editfly_tk = fondo_editfly_tk
titulo_editfly = ttk.Label(
    escena30,
    text="EDITAR VUELO",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_editfly.place(relx=0.5, rely=0.08, anchor="center")

buscar_vuelo_var = tk.StringVar()

edit_code_var = tk.StringVar(value="—")
edit_origen_var = tk.StringVar(value="—")
edit_destino_var = tk.StringVar(value="—")
edit_dia_var = tk.StringVar(value="—")
edit_hora_var = tk.StringVar(value="—")
edit_pref_var = tk.IntVar(value=10)
edit_econ_var = tk.IntVar(value=130)

lbl_edit_busc = ttk.Label(
    escena30,
    text="Ingrese código:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_edit_busc.place(relx=0.22, rely=0.20, anchor="w")

entry_edit_busc = ttk.Entry(
    escena30, textvariable=buscar_vuelo_var, width=25
)
entry_edit_busc.place(relx=0.45, rely=0.20, anchor="w")

style.configure("BuscarVuelo.TButton",
                font=("Triforce", 16, "bold"),
                background="#4ED3F1",
                foreground="black")

btn_busc_fly = ttk.Button(
    escena30,
    text="Buscar",
    style="BuscarVuelo.TButton",
    command=buscar_vuelo_editar
)
btn_busc_fly.place(relx=0.75, rely=0.20, anchor="center")


lbl_code_edit = ttk.Label(
    escena30, text="Código:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_code_edit.place(relx=0.22, rely=0.30, anchor="w")

entry_code_edit = ttk.Entry(
    escena30, textvariable=edit_code_var, width=35, state="disabled"
)
entry_code_edit.place(relx=0.47, rely=0.30, anchor="w")

lbl_ori_edit = ttk.Label(
    escena30, text="Origen:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_ori_edit.place(relx=0.22, rely=0.38, anchor="w")

combo_ori_edit = ttk.Combobox(
    escena30, textvariable=edit_origen_var,
    values=["ORNI", "ZORA", "GORON", "CASTILLO", "KAKARIKO", "HYLIA"],
    width=30, state="readonly"
)
combo_ori_edit.place(relx=0.47, rely=0.38, anchor="w")

lbl_dest_edit = ttk.Label(
    escena30, text="Destino:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_dest_edit.place(relx=0.22, rely=0.46, anchor="w")

combo_dest_edit = ttk.Combobox(
    escena30, textvariable=edit_destino_var,
    values=["ORNI", "ZORA", "GORON", "CASTILLO", "KAKARIKO", "HYLIA"],
    width=30, state="readonly"
)
combo_dest_edit.place(relx=0.47, rely=0.46, anchor="w")

lbl_dia_edit = ttk.Label(
    escena30, text="Día:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_dia_edit.place(relx=0.22, rely=0.54, anchor="w")

entry_dia_edit = ttk.Entry(
    escena30, textvariable=edit_dia_var, width=35
)
entry_dia_edit.place(relx=0.47, rely=0.54, anchor="w")

lbl_hora_edit = ttk.Label(
    escena30,
    text="Hora:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_hora_edit.place(relx=0.22, rely=0.62, anchor="w")

entry_hora_edit = ttk.Entry(
    escena30, textvariable=edit_hora_var, width=35
)
entry_hora_edit.place(relx=0.47, rely=0.62, anchor="w")

lbl_pref_edit = ttk.Label(
    escena30, text="Sillas preferenciales:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_pref_edit.place(relx=0.22, rely=0.70, anchor="w")

spin_pref_edit = ttk.Spinbox(
    escena30, from_=0, to=50, width=10, textvariable=edit_pref_var
)
spin_pref_edit.place(relx=0.47, rely=0.70, anchor="w")

lbl_econ_edit = ttk.Label(
    escena30, text="Sillas económicas:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_econ_edit.place(relx=0.22, rely=0.78, anchor="w")

spin_econ_edit = ttk.Spinbox(
    escena30, from_=0, to=200, width=10, textvariable=edit_econ_var
)
spin_econ_edit.place(relx=0.47, rely=0.78, anchor="w")

style.configure("VolverEditFly.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

btn_editfly_volver = ttk.Button(
    escena30,
    text="Volver",
    style="VolverEditFly.TButton",
    command=lambda: cambiar_escena(escena28)
)
btn_editfly_volver.place(relx=0.30, rely=0.88, anchor="center")

style.configure("SaveFly.TButton",
                font=("Triforce", 18, "bold"),
                background="#D4AF37",
                foreground="black")

btn_editfly_save = ttk.Button(
    escena30,
    text="Guardar Cambios",
    style="SaveFly.TButton",
    command= guardar_cambios_vuelo)
btn_editfly_save.place(relx=0.70, rely=0.88, anchor="center")

# ================================
# ESCENA 31 - ELIMINAR VUELO
# ================================
def buscar_vuelo_eliminar():
    codigo = del_fly_code_var.get().strip()

    if not codigo:
        messagebox.showerror("Error", "Ingrese un código de vuelo.")
        return

    encontrado = False

    try:
        with open("vuelos.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")

                if datos[0] == codigo:
                    encontrado = True

                    cod = datos[0]
                    ori = datos[1]
                    dest = datos[2]
                    fecha_completa = datos[3]
                    pref = datos[4]
                    econ = datos[5]

                    dd, mm, aa, hh, mn = fecha_completa.split("-")

                    del_code_var.set(cod)
                    del_origen_var.set(ori)
                    del_destino_var.set(dest)
                    del_dia_var.set(f"{dd}-{mm}-{aa}")
                    del_hora_var.set(f"{hh}:{mn}")
                    del_pref_var.set(pref)
                    del_econ_var.set(econ)

                    break
    except FileNotFoundError:
        messagebox.showerror("Error", "No existe el archivo vuelos.txt.")
        return

    if not encontrado:
        messagebox.showerror("Error", "Vuelo no encontrado.")

def eliminar_vuelo():
    cod = del_code_var.get()

    if cod == "—":
        messagebox.showerror("Error", "No se ha cargado ningún vuelo para eliminar.")
        return

    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Está seguro de eliminar el vuelo {cod}?"
    )

    if not confirmar:
        return

    nuevas_lineas = []
    eliminado = False

    try:
        with open("vuelos.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")
                if datos[0] == cod:
                    eliminado = True
                else:
                    nuevas_lineas.append(linea)
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo vuelos.txt no existe.")
        return

    if not eliminado:
        messagebox.showerror("Error", "Vuelo no encontrado en el archivo.")
        return

    try:
        with open("vuelos.txt", "w", encoding="utf-8") as f:
            for l in nuevas_lineas:
                f.write(l)
    except:
        messagebox.showerror("Error", "No se pudo escribir el archivo vuelos.txt.")
        return

    del_code_var.set("—")
    del_origen_var.set("—")
    del_destino_var.set("—")
    del_dia_var.set("—")
    del_hora_var.set("—")
    del_pref_var.set("—")
    del_econ_var.set("—")
    del_fly_code_var.set("")

    messagebox.showinfo("Éxito", f"Vuelo {cod} eliminado correctamente.")


escena31 = ttk.Frame(app)
escena31.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_delfly_img = Image.open("opciones_admin.jpg")
fondo_delfly_tk = ImageTk.PhotoImage(fondo_delfly_img)
tk.Label(escena31, image=fondo_delfly_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena31.fondo_delfly_tk = fondo_delfly_tk

titulo_delfly = ttk.Label(
    escena31,
    text="ELIMINAR VUELO",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_delfly.place(relx=0.5, rely=0.08, anchor="center")

del_fly_code_var = tk.StringVar()

del_code_var = tk.StringVar(value="—")
del_origen_var = tk.StringVar(value="—")
del_destino_var = tk.StringVar(value="—")
del_dia_var = tk.StringVar(value="—")
del_hora_var = tk.StringVar(value="—")
del_pref_var = tk.StringVar(value="—")
del_econ_var = tk.StringVar(value="—")

lbl_delfly_busc = ttk.Label(
    escena31,
    text="Ingrese código:",
    font=("Triforce",18),
    background="#16304C", foreground="white"
)
lbl_delfly_busc.place(relx=0.22, rely=0.20, anchor="w")

entry_delfly_busc = ttk.Entry(
    escena31, textvariable=del_fly_code_var, width=25
)
entry_delfly_busc.place(relx=0.45, rely=0.20, anchor="w")

style.configure("BuscarDelFly.TButton",
                font=("Triforce", 16, "bold"),
                background="#4ED3F1",
                foreground="black")

btn_delfly_busc = ttk.Button(
    escena31,
    text="Buscar",
    style="BuscarDelFly.TButton",
    command= buscar_vuelo_eliminar
)
btn_delfly_busc.place(relx=0.75, rely=0.20, anchor="center")

lbl_delfly_code = ttk.Label(
    escena31, text="Código:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_delfly_code.place(relx=0.22, rely=0.30, anchor="w")

entry_delfly_code = ttk.Entry(
    escena31, textvariable=del_code_var, width=35, state="disabled"
)
entry_delfly_code.place(relx=0.47, rely=0.30, anchor="w")

lbl_delfly_orig = ttk.Label(
    escena31, text="Origen:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_delfly_orig.place(relx=0.22, rely=0.38, anchor="w")

entry_delfly_orig = ttk.Entry(
    escena31, textvariable=del_origen_var, width=35, state="disabled"
)
entry_delfly_orig.place(relx=0.47, rely=0.38, anchor="w")

lbl_delfly_dest = ttk.Label(
    escena31, text="Destino:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_delfly_dest.place(relx=0.22, rely=0.46, anchor="w")

entry_delfly_dest = ttk.Entry(
    escena31, textvariable=del_destino_var, width=35, state="disabled"
)
entry_delfly_dest.place(relx=0.47, rely=0.46, anchor="w")

lbl_delfly_dia = ttk.Label(
    escena31, text="Día:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_delfly_dia.place(relx=0.22, rely=0.54, anchor="w")

entry_delfly_dia = ttk.Entry(
    escena31, textvariable=del_dia_var, width=35, state="disabled"
)
entry_delfly_dia.place(relx=0.47, rely=0.54, anchor="w")

lbl_delfly_hora = ttk.Label(
    escena31, text="Hora:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_delfly_hora.place(relx=0.22, rely=0.62, anchor="w")

entry_delfly_hora = ttk.Entry(
    escena31, textvariable=del_hora_var, width=35, state="disabled"
)
entry_delfly_hora.place(relx=0.47, rely=0.62, anchor="w")

lbl_delfly_pref = ttk.Label(
    escena31, text="Preferencial:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_delfly_pref.place(relx=0.22, rely=0.70, anchor="w")

entry_delfly_pref = ttk.Entry(
    escena31, textvariable=del_pref_var, width=35, state="disabled"
)
entry_delfly_pref.place(relx=0.47, rely=0.70, anchor="w")

lbl_delfly_econ = ttk.Label(
    escena31, text="Económicas:",
    font=("Triforce", 18),
    background="#16304C", foreground="white"
)
lbl_delfly_econ.place(relx=0.22, rely=0.78, anchor="w")

entry_delfly_econ = ttk.Entry(
    escena31, textvariable=del_econ_var, width=35, state="disabled"
)
entry_delfly_econ.place(relx=0.47, rely=0.78, anchor="w")

msg_del_warning = ttk.Label(
    escena31,
    text="⚠ Esta acción eliminará el vuelo permanentemente.",
    font=("Triforce", 20),
    background="#8B0000",
    foreground="white"
)
msg_del_warning.place(relx=0.5, rely=0.85, anchor="center")

style.configure("VolverDelFly.TButton",
                font=("Triforce", 18, "bold"),
                background="#4C7A46",
                foreground="white")

btn_delfly_volver = ttk.Button(
    escena31,
    text="Volver",
    style="VolverDelFly.TButton",
    command=lambda: cambiar_escena(escena28)
)
btn_delfly_volver.place(relx=0.30, rely=0.92, anchor="center")

style.configure("EliminarFly.TButton",
                font=("Triforce", 18, "bold"),
                background="#B22222",
                foreground="white")

btn_delfly_eliminar = ttk.Button(
    escena31,
    text="Eliminar Vuelo",
    style="EliminarFly.TButton",
    command=eliminar_vuelo
)
btn_delfly_eliminar.place(relx=0.70, rely=0.92, anchor="center")

# ================================
# ESCENA 32 - VER VUELOS
# ================================

def cargar_vuelos_tabla():
    tabla_vuelos.delete(*tabla_vuelos.get_children())

    try:
        with open("vuelos.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")

                if len(datos) < 7:
                    continue

                codigo = datos[0]
                origen = datos[1]
                destino = datos[2]
                fecha_completa = datos[3]

                try:
                    dd, mm, aa, hh, mn = fecha_completa.split("-")
                    dia = f"{dd}-{mm}-{aa}"
                    hora = f"{hh}:{mn}"
                except:
                    dia = "—"
                    hora = "—"

                pref = datos[4]
                econ = datos[5]

                tabla_vuelos.insert(
                    "",
                    "end",
                    values=(codigo, origen, destino, dia, hora, pref, econ)
                )

    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo vuelos.txt no existe.")
    except Exception as e:
        messagebox.showerror("Error", f"No fue posible cargar los vuelos:\n{e}")


escena32 = ttk.Frame(app)
escena32.place(relx=0, rely=0, relwidth=1, relheight=1)

# Fondo
fondo_vervuelos_img = Image.open("opciones_admin.jpg")
fondo_vervuelos_tk = ImageTk.PhotoImage(fondo_vervuelos_img)
tk.Label(escena32, image=fondo_vervuelos_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena32.fondo_vervuelos_tk = fondo_vervuelos_tk

titulo_vervuelos = ttk.Label(
    escena32,
    text="LISTA DE VUELOS",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_vervuelos.place(relx=0.5, rely=0.08, anchor="center")

cols_vuelos = ("codigo", "origen", "destino", "dia", "hora", "pref", "econ")

tabla_vuelos = ttk.Treeview(
    escena32,
    columns=cols_vuelos,
    show="headings",
    height=18
)

tabla_vuelos.heading("codigo", text="Código")
tabla_vuelos.heading("origen", text="Origen")
tabla_vuelos.heading("destino", text="Destino")
tabla_vuelos.heading("dia", text="Día")
tabla_vuelos.heading("hora", text="Hora")
tabla_vuelos.heading("pref", text="Pref.")
tabla_vuelos.heading("econ", text="Econ.")

tabla_vuelos.column("codigo", width=120, anchor="center")
tabla_vuelos.column("origen", width=120, anchor="center")
tabla_vuelos.column("destino", width=120, anchor="center")
tabla_vuelos.column("dia", width=120, anchor="center")
tabla_vuelos.column("hora", width=100, anchor="center")
tabla_vuelos.column("pref", width=80, anchor="center")
tabla_vuelos.column("econ", width=80, anchor="center")


tabla_vuelos.place(relx=0.5, rely=0.50, anchor="center")

style.configure("VolverVerVuelos.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

def ir_a_escena32():
    cargar_vuelos_tabla()
    cambiar_escena(escena32)

btn_vervuelos_volver = ttk.Button(
    escena32,
    text="Volver",
    style="VolverVerVuelos.TButton",
    command=lambda: cambiar_escena(escena28)
)
btn_vervuelos_volver.place(relx=0.5, rely=0.90, anchor="center")

# ================================
# ESCENA 33 - VER RESERVAS
# ================================
def cargar_reservas_tabla():
    tabla_reservas.delete(*tabla_reservas.get_children())

    try:
        vuelos = {}
        with open("vuelos.txt", "r", encoding="utf-8") as f:
            for linea in f:
                d = linea.strip().split(",")
                if len(d) >= 7:
                    codigo = d[0]
                    fecha = d[3]
                    try:
                        dd, mm, aa, hh, mn = fecha.split("-")
                        fecha_limpia = f"{dd}-{mm}-{aa}"
                    except:
                        fecha_limpia = "—"
                    vuelos[codigo] = fecha_limpia

        with open("reservas.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")
                if len(datos) != 12:
                    continue  

                codigo_res = datos[0]
                usuario = datos[1]
                codigo_vuelo = datos[2]
                tipo = datos[4].capitalize()
                asiento = datos[5]
                estado_raw = datos[11]

                estados = {
                    "0": "Activa",
                    "1": "Check-in",
                    "2": "Cancelada"
                }
                estado = estados.get(estado_raw, estado_raw)

                fecha = vuelos.get(codigo_vuelo, "—")

                tabla_reservas.insert(
                    "",
                    "end",
                    values=(codigo_res, usuario, codigo_vuelo, fecha, asiento, tipo, estado)
                )

    except Exception as e:
        messagebox.showerror("Error", f"No fue posible cargar reservas:\n{e}")

escena33 = ttk.Frame(app)
escena33.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_verres_img = Image.open("opciones_admin.jpg")
fondo_verres_tk = ImageTk.PhotoImage(fondo_verres_img)
tk.Label(escena33, image=fondo_verres_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena33.fondo_verres_tk = fondo_verres_tk

titulo_verres = ttk.Label(
    escena33,
    text="RESERVAS DEL SISTEMA",
    font=("Triforce", 34, "bold"),
    background="#16304C",
    foreground="white"
)
titulo_verres.place(relx=0.5, rely=0.08, anchor="center")

cols_reservas = ("codigo", "usuario", "vuelo", "fecha", "asiento", "tipo", "estado")

tabla_reservas = ttk.Treeview(
    escena33,
    columns=cols_reservas,
    show="headings",
    height=18
)

tabla_reservas.heading("codigo", text="Código Reserva")
tabla_reservas.heading("usuario", text="Usuario")
tabla_reservas.heading("vuelo", text="Vuelo")
tabla_reservas.heading("fecha", text="Fecha")
tabla_reservas.heading("asiento", text="Asiento")
tabla_reservas.heading("tipo", text="Tipo")
tabla_reservas.heading("estado", text="Estado")

tabla_reservas.column("codigo", width=160, anchor="center")
tabla_reservas.column("usuario", width=150, anchor="center")
tabla_reservas.column("vuelo", width=120, anchor="center")
tabla_reservas.column("fecha", width=120, anchor="center")
tabla_reservas.column("asiento", width=80, anchor="center")
tabla_reservas.column("tipo", width=100, anchor="center")
tabla_reservas.column("estado", width=130, anchor="center")

tabla_reservas.place(relx=0.5, rely=0.50, anchor="center")

style.configure("VolverReservas.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

def ir_a_escena33():
    cargar_reservas_tabla()
    cambiar_escena(escena33)

btn_reservas_volver = ttk.Button(
    escena33,
    text="Volver",
    style="VolverReservas.TButton",
    command=lambda: cambiar_escena(escena22)
)
btn_reservas_volver.place(relx=0.5, rely=0.92, anchor="center")

# ================================
# ESCENA 34 – ESTADÍSTICAS
# ================================
escena34 = ttk.Frame(app)
escena34.place(relx=0, rely=0, relwidth=1, relheight=1)

fondo_stats_img = Image.open("opciones_usuario.png")
fondo_stats_tk = ImageTk.PhotoImage(fondo_stats_img)
tk.Label(escena34, image=fondo_stats_tk).place(x=0, y=0, relwidth=1, relheight=1)
escena34.fondo_stats_tk = fondo_stats_tk

titulo_stats = ttk.Label(
    escena34,
    text="ESTADÍSTICAS DEL SISTEMA",
    font=("Triforce", 30, "bold"),
    background="#16304C",
    foreground="white",
    padding=10
)
titulo_stats.place(relx=0.5, rely=0.07, anchor="center")

frame_stats = tk.Frame(
    escena34,
    bg="#16304C",
    highlightbackground="gold",
    highlightthickness=3
)
frame_stats.place(relx=0.5, rely=0.34, anchor="center", width=600, height=250)

# VARIABLES
stats_total_usuarios = tk.StringVar()
stats_total_vuelos   = tk.StringVar()
stats_total_reservas = tk.StringVar()
stats_vuelo_popular  = tk.StringVar()

font_label = ("Triforce", 18)
font_value = ("Triforce", 18, "bold")

items = [
    ("Total Usuarios:", stats_total_usuarios),
    ("Total Vuelos:", stats_total_vuelos),
    ("Total Reservas:", stats_total_reservas),
    ("Vuelo más reservado:", stats_vuelo_popular),
]

y_offset = 0.15
for texto, variable in items:
    lbl = ttk.Label(frame_stats, text=texto, font=font_label,
                    background="#16304C", foreground="white")
    lbl.place(relx=0.05, rely=y_offset)

    val = ttk.Label(frame_stats, textvariable=variable, font=font_value,
                    background="#16304C", foreground="gold")
    val.place(relx=0.70, rely=y_offset)

    y_offset += 0.20

img_stats_graph = Image.open("grafica.jpg").resize((600, 200))
img_stats_graph_tk = ImageTk.PhotoImage(img_stats_graph)
lbl_stats_graph = tk.Label(escena34, image=img_stats_graph_tk, bg="#000000")
lbl_stats_graph.place(relx=0.5, rely=0.7, anchor="center")
escena34.img_stats_graph_tk = img_stats_graph_tk

style.configure("VolverStats.TButton",
                font=("Triforce", 18, "bold"),
                background="#8B0000",
                foreground="white")

btn_stats_volver = ttk.Button(
    escena34,
    text="Volver",
    style="VolverStats.TButton",
    command=lambda: cambiar_escena(escena22)
)
btn_stats_volver.place(relx=0.5, rely=0.93, anchor="center")





app.after(0, mostrar_mensaje)
escena1.tkraise()

reproducir_musica("musica_incio.mp3")
app.mainloop()
