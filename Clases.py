class Fecha:
    def __init__(self, dd=0, mm=0, aa=0, hh=0, min=0):
        self.__dd = dd
        self.__mm = mm
        self.__aa = aa
        self.__hh = hh
        self.__min = min

    def getDD(self):
        return self.__dd

    def getMM(self):
        return self.__mm

    def getAA(self):
        return self.__aa

    def getHH(self):
        return self.__hh

    def getMIN(self):
        return self.__min

    def setDD(self, dd):
        self.__dd = dd

    def setMM(self, mm):
        self.__mm = mm

    def setAA(self, aa):
        self.__aa = aa

    def setHH(self, hh):
        self.__hh = hh

    def setMIN(self, min):
        self.__min = min

    def __str__(self):
        return f"{self.__dd}-{self.__mm}-{self.__aa}  {self.__hh}:{self.__min}"


from abc import ABC


class Persona(ABC):
    def __init__(self, nombre="", email="", id=0, contrasena=""):
        self.__nombre = nombre
        self.__id = id
        self.__email = email
        self.__contrasena = contrasena

    def getNombre(self):
        return self.__nombre

    def getId(self):
        return self.__id

    def getEmail(self):
        return self.__email

    def getContrasena(self):
        return self.__contrasena

    def setNombre(self, n):
        self.__nombre = n

    def setEmail(self, e):
        self.__email = e

    def setId(self, id):
        self.__id = id

    def setContrasena(self, c):
        self.__contrasena = c

    def cambiarContrasena(self, nueva):
        self.__contrasena = nueva


class Usuario(Persona):
    def __init__(self, nombre="", email="", id=0, contrasena=""):
        super().__init__(nombre, email, id, contrasena)
        self.__millas = 0
        self.__reservasHechas = []

    def getMillas(self):
        return self.__millas

    def getReservasHechas(self):
        return self.__reservasHechas

    def agregarReservaU(self, reserva):
        self.__reservasHechas.append(reserva)

    def eliminarReservaU(self, reserva):
        if reserva in self.__reservasHechas:
            self.__reservasHechas.remove(reserva)
            return True
        return False

    def acumularMillas(self, m):
        self.__millas += m

    def restarMillas(self, m):
        if m <= self.__millas:
            self.__millas -= m
            return True
        return False

    def MillasPreferencial(self):
        return self.__millas >= 2000

    def __str__(self):
        return f"Usuario: {self.getNombre()} - ID: {self.getId()} - Email: {self.getEmail()} - Millas: {self.__millas}"


class Admin(Persona):
    def __init__(self, nombre="", email="", id=0, contrasena=""):
        super().__init__(nombre, email, id, contrasena)

    def agregarUsuario(self, sistema, usuario):
        sistema.agregarUsuario(usuario)

    def editarUsuario(self, sistema, idUsuario, actualizado):
        sistema.editarUsuario(idUsuario, actualizado)

    def buscarUsuario(self, sistema, idUsuario):
        return sistema.buscarUsuario(idUsuario)

    def eliminarUsuario(self, sistema, idUsuario):
        sistema.eliminarUsuario(idUsuario)

    def modificarVuelo(self, sistema, idVuelo, actualizado):
        sistema.modificarVuelo(idVuelo, actualizado)

    def agregarVuelo(self, sistema, vuelo):
        sistema.agregarVuelo(vuelo)

    def buscarVuelo(self, sistema, idVuelo):
        return sistema.buscarVuelo(idVuelo)

    def eliminarVuelo(self, sistema, idVuelo):
        sistema.eliminarVuelo(idVuelo)

    def buscarVuelos(self, sistema, co, cd):
        return sistema.buscarVuelos(co, cd)

    def verVuelos(self, sistema):
        return sistema.verVuelos()

    def verUsuarios(self, sistema):
        return sistema.verUsuarios()

    def verReservas(self, sistema):
        return sistema.verReservas()


class Vuelo:
    def __init__(self, id="", ciudadOrigen="", ciudadDestino="", horario=None, sillasPref=0, sillasEco=0, disponibilidad=True):
        if horario is None:
            horario = Fecha()
        self.__id = id
        self.__ciudadOrigen = ciudadOrigen
        self.__ciudadDestino = ciudadDestino
        self.__horario = horario
        self.__sillasPref = sillasPref
        self.__sillasEco = sillasEco
        self.__disponibilidad = disponibilidad

    def getId(self):
        return self.__id

    def getCiudadOrigen(self):
        return self.__ciudadOrigen

    def getCiudadDestino(self):
        return self.__ciudadDestino

    def getHorario(self):
        return self.__horario

    def getSillasPref(self):
        return self.__sillasPref

    def getSillasEco(self):
        return self.__sillasEco

    def getDisponibilidad(self):
        return self.__disponibilidad

    def setCiudadOrigen(self, co):
        self.__ciudadOrigen = co

    def setCiudadDestino(self, cd):
        self.__ciudadDestino = cd

    def setHorario(self, h):
        self.__horario = h

    def setSillasPref(self, sp):
        self.__sillasPref = sp

    def setSillasEco(self, se):
        self.__sillasEco = se

    def setDisponibilidad(self, d):
        self.__disponibilidad = d

    def agregarSillasPref(self, n):
        self.__sillasPref += n
        self.actualizarDisponibilidad()

    def agregarSillasEco(self, n):
        self.__sillasEco += n
        self.actualizarDisponibilidad()

    def restarSillasPref(self, n):
        self.__sillasPref -= n
        if self.__sillasPref < 0:
            self.__sillasPref = 0
        self.actualizarDisponibilidad()

    def restarSillasEco(self, n):
        self.__sillasEco -= n
        if self.__sillasEco < 0:
            self.__sillasEco = 0
        self.actualizarDisponibilidad()

    def actualizarDisponibilidad(self):
        self.__disponibilidad = (self.__sillasEco > 0 or self.__sillasPref > 0)

    def getFecha(self):
        return self.__horario

    def __str__(self):
        return f"Vuelo {self.__id}: {self.__ciudadOrigen} - {self.__ciudadDestino} ({self.__horario}, Disponibilidad: {self.__disponibilidad})"


class Pasajero:
    def __init__(self, nombre="", id=0):
        self.__nombre = nombre
        self.__id = id

    def getNombre(self):
        return self.__nombre

    def getId(self):
        return self.__id

    def setNombre(self, n):
        self.__nombre = n

    def setId(self, i):
        self.__id = i

    def __str__(self):
        return f"Nombre: {self.__nombre}, Documento: {self.__id}"


class Reserva:
    precioPref = 850000
    precioEco = 235000
    precioMano = 0
    precioCabina = 40000
    precioBodega = 90000

    def __init__(self, id="", idUsuario=0, idVuelo="", pasajeros=None, tipoSilla="", cantidadSillas=0, equipajeCabina=0, equipajeBodega=0, equipajeMano=0, precioTotal=0, checkInHecho=False, estadoReserva="Activa"):
        if pasajeros is None:
            pasajeros = []
        self.__id = id
        self.__idUsuario = idUsuario
        self.__idVuelo = idVuelo
        self.__pasajeros = pasajeros
        self.__tipoSilla = tipoSilla.lower()
        self.__cantidadSillas = cantidadSillas
        self.__equipajeCabina = equipajeCabina
        self.__equipajeBodega = equipajeBodega
        self.__equipajeMano = equipajeMano
        self.__precioTotal = precioTotal
        self.__checkInHecho = checkInHecho
        self.__estadoReserva = estadoReserva

    def getId(self):
        return self.__id

    def getIdUsuario(self):
        return self.__idUsuario

    def getIdVuelo(self):
        return self.__idVuelo

    def getPasajeros(self):
        return self.__pasajeros

    def getTipoSilla(self):
        return self.__tipoSilla

    def getCantidadSillas(self):
        return self.__cantidadSillas

    def getEquipajeCabina(self):
        return self.__equipajeCabina

    def getEquipajeBodega(self):
        return self.__equipajeBodega

    def getEquipajeMano(self):
        return self.__equipajeMano
    
    def getPrecioTotal(self):
        return self.__precioTotal

    def getEstado(self):
        return self.__estadoReserva

    def getCheckIn(self):
        return self.__checkInHecho

    def setPasajeros(self, p):
        self.__pasajeros = p

    def setTipoSilla(self, t):
        self.__tipoSilla = t.lower()

    def setCantidadSillas(self, c):
        self.__cantidadSillas = c

    def setEquipajeCabina(self, n):
        self.__equipajeCabina = n

    def setEquipajeBodega(self, n):
        self.__equipajeBodega = n

    def setEquipajeMano(self, n):
        self.__equipajeMano = n

    def setEstado(self, e):
        self.__estadoReserva = e

    def setCheckIn(self, c):
        self.__checkInHecho = c

    def validarPasajeros(self):
        return len(self.__pasajeros) <= 3

    def calcularPrecioSillas(self):
        if self.__tipoSilla == "preferencial":
            return self.__cantidadSillas * Reserva.precioPref
        return self.__cantidadSillas * Reserva.precioEco

    def calcularPrecioEquipaje(self):
        precio = 0
        precio += self.__equipajeMano * Reserva.precioMano
        precio += self.__equipajeCabina * Reserva.precioCabina
        precio += self.__equipajeBodega * Reserva.precioBodega
        return precio

    def calcularPrecioTotal(self):
        total = self.calcularPrecioSillas() + self.calcularPrecioEquipaje()
        self.__precioTotal = total
        return total

    def hacerCheckIn(self):
        if self.__estadoReserva == "Cancelada":
            return False
        self.__checkInHecho = True
        self.__estadoReserva = "Check-in"
        return True

    def cancelarReserva(self):
        if self.__checkInHecho:
            return False
        self.__estadoReserva = "Cancelada"
        return True

    def esModificable(self):
        return not self.__checkInHecho and self.__estadoReserva == "Activa"

    def modificarReserva(self, nuevoTipo="", nuevasSillas=0, nuevoCabina=0, nuevoBodega=0, nuevoMano=0, nuevosPasajeros=None):
        if self.__checkInHecho:
            return False
        if nuevosPasajeros is not None:
            if len(nuevosPasajeros) > 3:
                return False
            self.__pasajeros = nuevosPasajeros
        if nuevoTipo != "":
            self.__tipoSilla = nuevoTipo.lower()
        if nuevasSillas > 0:
            self.__cantidadSillas = nuevasSillas
        self.__equipajeCabina = nuevoCabina
        self.__equipajeBodega = nuevoBodega
        self.__equipajeMano = nuevoMano
        self.calcularPrecioTotal()
        return True

    def __str__(self):
        return f"Reserva {self.__id} - Usuario {self.__idUsuario} - Vuelo {self.__idVuelo} - Estado: {self.__estadoReserva} - Total: {self.__precioTotal}"


class Sistema:
    def __init__(self):
        self.__usuarios = []
        self.__admins = []
        self.__vuelos = []
        self.__reservas = []

    def agregarUsuario(self, usuario):
        for u in self.__usuarios:
            if u.getId() == usuario.getId():
                return False
        self.__usuarios.append(usuario)
        return True

    def buscarUsuario(self, idUsuario):
        for u in self.__usuarios:
            if u.getId() == idUsuario:
                return u
        return None

    def editarUsuario(self, idUsuario, actualizado):
        for i, u in enumerate(self.__usuarios):
            if u.getId() == idUsuario:
                self.__usuarios[i] = actualizado
                return True
        return False

    def eliminarUsuario(self, idUsuario):
        for u in self.__usuarios:
            if u.getId() == idUsuario:
                self.__usuarios.remove(u)
                return True
        return False

    def verUsuarios(self):
        return self.__usuarios

    def agregarAdmin(self, admin):
        for a in self.__admins:
            if a.getId() == admin.getId():
                return False
        self.__admins.append(admin)
        return True

    def buscarAdmin(self, idAdmin):
        for a in self.__admins:
            if a.getId() == idAdmin:
                return a
        return None

    def iniciarSesion(self, idUsuario, contrasena):
        # Buscar en usuarios
        for u in self.__usuarios:
            if u.getId() == idUsuario and u.getContrasena() == contrasena:
                return u
        
        # Buscar en admins
        for a in self.__admins:
            if a.getId() == idUsuario and a.getContrasena() == contrasena:
                return a
        
        return None

    def agregarVuelo(self, vuelo):
        for v in self.__vuelos:
            if v.getId() == vuelo.getId():
                return False
        self.__vuelos.append(vuelo)
        return True

    def buscarVuelo(self, idVuelo):
        for v in self.__vuelos:
            if v.getId() == idVuelo:
                return v
        return None

    def modificarVuelo(self, idVuelo, actualizado):
        for i, v in enumerate(self.__vuelos):
            if v.getId() == idVuelo:
                self.__vuelos[i] = actualizado
                return True
        return False

    def eliminarVuelo(self, idVuelo):
        for v in self.__vuelos:
            if v.getId() == idVuelo:
                for r in self.__reservas:
                    if r.getIdVuelo() == idVuelo:
                        return False
                self.__vuelos.remove(v)
                return True
        return False

    def verVuelos(self):
        return self.__vuelos

    def buscarVuelos(self, origen, destino):
        resultado = []
        for v in self.__vuelos:
            if v.getCiudadOrigen() == origen and v.getCiudadDestino() == destino:
                resultado.append(v)
        return resultado

    def agregarReserva(self, reserva):
        for r in self.__reservas:
            if r.getId() == reserva.getId():
                return False
        vuelo = self.buscarVuelo(reserva.getIdVuelo())
        if vuelo is None:
            return False
        usuario = self.buscarUsuario(reserva.getIdUsuario())
        if usuario is None:
            return False

        tipo = reserva.getTipoSilla()

        # ---- BENEFICIO DE MILLAS ----
        usar_millas = False
        if tipo == "preferencial" and usuario.getMillas() >= 2000:
            usar_millas = True

        # ---- Disponibilidad ----
        if tipo == "preferencial":
            if reserva.getCantidadSillas() > vuelo.getSillasPref():
                return False
            vuelo.restarSillasPref(reserva.getCantidadSillas())
        else:
            if reserva.getCantidadSillas() > vuelo.getSillasEco():
                return False
            vuelo.restarSillasEco(reserva.getCantidadSillas())

        vuelo.actualizarDisponibilidad()

        # ---- Precio ----
        if usar_millas:
            usuario.restarMillas(2000)          # se descuentan millas
            reserva.setTipoSilla("economica")   # se cobra como económica

        reserva.calcularPrecioTotal()
        self.__reservas.append(reserva)

        # ---- Millas por la reserva ----
        usuario.agregarReservaU(reserva)
        usuario.acumularMillas(500)

        return True

    def buscarReserva(self, idReserva):
        for r in self.__reservas:
            if r.getId() == idReserva:
                return r
        return None

    def verReservas(self):
        return self.__reservas

    def modificarReserva(self, idReserva, nuevosDatos):
        reserva = self.buscarReserva(idReserva)
        if reserva is None:
            return False

        if not reserva.esModificable():
            return False

        vuelo = self.buscarVuelo(reserva.getIdVuelo())
        if vuelo is None:
            return False

        usuario = self.buscarUsuario(reserva.getIdUsuario())

        # Guardamos datos anteriores ANTES de modificar
        tipo_anterior = reserva.getTipoSilla()
        sillas_anteriores = reserva.getCantidadSillas()

        # 1. Devolver sillas antiguas al vuelo
        if tipo_anterior == "preferencial":
            vuelo.agregarSillasPref(sillas_anteriores)
        else:
            vuelo.agregarSillasEco(sillas_anteriores)

        nuevas_sillas = nuevosDatos["sillas"]
        nuevo_tipo = nuevosDatos["tipo"].lower()

        # ---------------------------------------
        #   BENEFICIO DE MILLAS PREFERENCIAL
        # ---------------------------------------
        usar_millas = False
        if nuevo_tipo == "preferencial" and usuario.getMillas() >= 2000:
            usar_millas = True

        # 2. Validar disponibilidad para el nuevo tipo
        if nuevo_tipo == "preferencial":
            if nuevas_sillas > vuelo.getSillasPref():
                # Revertir devolución
                if tipo_anterior == "preferencial":
                    vuelo.restarSillasPref(sillas_anteriores)
                else:
                    vuelo.restarSillasEco(sillas_anteriores)
                return False
        else:
            if nuevas_sillas > vuelo.getSillasEco():
                if tipo_anterior == "preferencial":
                    vuelo.restarSillasPref(sillas_anteriores)
                else:
                    vuelo.restarSillasEco(sillas_anteriores)
                return False

        # 3. Intentar modificar la reserva
        ok = reserva.modificarReserva(
            nuevoTipo=nuevo_tipo,
            nuevasSillas=nuevas_sillas,
            nuevoCabina=nuevosDatos["cabina"],
            nuevoBodega=nuevosDatos["bodega"],
            nuevoMano=nuevosDatos["mano"],
            nuevosPasajeros=nuevosDatos["pasajeros"]
        )

        if not ok:
            # Revertir por error de modificación
            if tipo_anterior == "preferencial":
                vuelo.restarSillasPref(sillas_anteriores)
            else:
                vuelo.restarSillasEco(sillas_anteriores)
            return False

        # 4. Aplicar la nueva resta
        if nuevo_tipo == "preferencial":
            vuelo.restarSillasPref(nuevas_sillas)
        else:
            vuelo.restarSillasEco(nuevas_sillas)

        vuelo.actualizarDisponibilidad()

        # ---------------------------------------
        #   DESCONTAR MILLAS SI SE USÓ EL BENEFICIO
        # ---------------------------------------
        if usar_millas:
            usuario.restarMillas(2000)
            reserva.setTipoSilla("economica")
            reserva.calcularPrecioTotal()

        return True

    def cancelarReserva(self, idReserva):
        reserva = self.buscarReserva(idReserva)
        if reserva is None:
            return False
        if reserva.getCheckIn():
            return False
        vuelo = self.buscarVuelo(reserva.getIdVuelo())
        if vuelo:
            if reserva.getTipoSilla() == "preferencial":
                vuelo.agregarSillasPref(reserva.getCantidadSillas())
            else:
                vuelo.agregarSillasEco(reserva.getCantidadSillas())
        reserva.setEstado("Cancelada")
        vuelo.actualizarDisponibilidad()
        return True

    def hacerCheckIn(self, idReserva):
        reserva = self.buscarReserva(idReserva)
        if reserva is None:
            return False
        return reserva.hacerCheckIn()

    def totalUsuarios(self):
        return len(self.__usuarios)

    def totalVuelos(self):
        return len(self.__vuelos)

    def totalReservas(self):
        return len(self.__reservas)

    def vueloMasReservado(self):
        contador = {}
        for r in self.__reservas:
            v = r.getIdVuelo()
            contador[v] = contador.get(v, 0) + 1
        if not contador:
            return None
        mas = max(contador, key=contador.get)
        return mas
    
    def guardarInfo(self):
        # Guardar usuarios
        with open("usuarios.txt", "w", encoding="utf-8") as f:
            for u in self.__usuarios:
                f.write(f"{u.getId()},{u.getNombre()},{u.getEmail()},{u.getContrasena()},{u.getMillas()}\n")

        # Guardar admins
        with open("admins.txt", "w", encoding="utf-8") as f:
            for a in self.__admins:
                f.write(f"{a.getId()},{a.getNombre()},{a.getEmail()},{a.getContrasena()}\n")

        # Guardar vuelos
        with open("vuelos.txt", "w", encoding="utf-8") as f:
            for v in self.__vuelos:
                hor = v.getHorario()
                f.write(f"{v.getId()},{v.getCiudadOrigen()},{v.getCiudadDestino()},{hor.getDD()}-{hor.getMM()}-{hor.getAA()}-{hor.getHH()}-{hor.getMIN()},{v.getSillasPref()},{v.getSillasEco()},{v.getDisponibilidad()}\n")

        # Guardar reservas
        with open("reservas.txt", "w", encoding="utf-8") as f:
            for r in self.__reservas:
                pasajeros_str = ";".join([f"{p.getNombre()}-{p.getId()}" for p in r.getPasajeros()])
                f.write(f"{r.getId()},{r.getIdUsuario()},{r.getIdVuelo()},{pasajeros_str},{r.getTipoSilla()},{r.getCantidadSillas()},{r.getEquipajeCabina()},{r.getEquipajeBodega()},{r.getEquipajeMano()},{r.getPrecioTotal()},{r.getCheckIn()},{r.getEstado()}\n")
    def cargarInfo(self):
        from os.path import exists

        # ----- USUARIOS -----
        if exists("usuarios.txt"):
            with open("usuarios.txt", "r", encoding="utf-8") as f:
                for linea in f:
                    id, nombre, email, contrasena, millas = linea.strip().split(",")
                    u = Usuario(nombre, email, int(id), contrasena)
                    u.acumularMillas(int(millas))
                    self.__usuarios.append(u)

        # ----- ADMINS -----
        if exists("admins.txt"):
            with open("admins.txt", "r", encoding="utf-8") as f:
                for linea in f:
                    id, nombre, email, contrasena = linea.strip().split(",")
                    a = Admin(nombre, email, int(id), contrasena)
                    self.__admins.append(a)

        # ----- VUELOS -----
        if exists("vuelos.txt"):
            with open("vuelos.txt", "r", encoding="utf-8") as f:
                for linea in f:
                    id, co, cd, fecha_str, sp, se, disp = linea.strip().split(",")
                    dd, mm, aa, hh, mn = fecha_str.split("-")
                    fecha = Fecha(int(dd), int(mm), int(aa), int(hh), int(mn))
                    v = Vuelo(id, co, cd, fecha, int(sp), int(se), disp == "True")
                    self.__vuelos.append(v)

        # ----- RESERVAS -----
        if exists("reservas.txt"):
            with open("reservas.txt", "r", encoding="utf-8") as f:
                for linea in f:
                    datos = linea.strip().split(",")
                    idR, idU, idV = datos[0], int(datos[1]), datos[2]
                    pasajeros_raw = datos[3]
                    tipo, cant, cab, bod, man, total, check, estado = datos[4:]

                    pasajeros = []
                    if pasajeros_raw != "":
                        for p in pasajeros_raw.split(";"):
                            nom, doc = p.split("-")
                            pasajeros.append(Pasajero(nom, int(doc)))

                    r = Reserva(idR, idU, idV, pasajeros, tipo, int(cant),
                                int(cab), int(bod), int(man), float(total),
                                check == "True", estado)

                    self.__reservas.append(r)

                    # También agregamos las reservas al usuario:
                    u = self.buscarUsuario(idU)
                    if u:
                        u.agregarReservaU(r)