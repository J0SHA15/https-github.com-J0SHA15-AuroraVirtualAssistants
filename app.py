from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import unidecode
import string
import random
import subprocess

app = Flask(__name__)

intents = [
    {
            "tag": "saludo",
        "patterns": [
            "Hola",
            "¿Cómo estás?",
            "¿Hay alguien ahí?",
            "Hola",
            "Hola",
            "Buen día",
            "Namaste",
            "¡Hola!"
        ],
        "responses": [
            "Hola",
            "¡Qué bueno verte de nuevo!",
            "Hola, ¿cómo puedo ayudarte?"
        ]
    },
    {
        "tag": "agradecimiento",
        "patterns": [
            "Gracias",
            "Eso es útil",
            "Genial, gracias",
            "Gracias por ayudarme"
        ],
        "responses": [
            "¡Feliz de poder ayudar!",
            "¡Cualquier momento!",
            "Es un placer"
        ]
    },
        {
            "tag": "sin_respuesta",
            "patterns": [],
            "responses": [
                "Lo siento, no puedo entenderte",
                "Por favor, dame más información",
                "No estoy segura de entender",
                "Lo siento, no estoy seguro de entender. ¿Puedes reformular tu pregunta?"
            ],
            "context": [""]
        },
        {
            "tag": "opciones",
            "patterns": [
                "¿Cómo puedes ayudarme?",
                "¿Qué puedes hacer?",
                "¿Qué ayuda proporcionas?",
                "¿Cómo puedes ser útil?",
                "¿Qué soporte se ofrece?"
            ],
            "responses": [
                "Soy una Asistente virtual de propósito general. Mis capacidades son:\n1. Puedo chatear contigo. ¡Intenta pedirme chistes o acertijos!\n2. Puedo obtener el clima actual para cualquier ciudad. Usa el formato weather: nombre de la ciudad.\n3. Puedo obtener las 10 noticias más populares en India. Usa las palabras clave 'Últimas noticias'.\n4. Puedo obtener las 10 canciones más populares a nivel mundial. Escribe 'canciones'.\n5. Puedo configurar un temporizador para ti. Ingresa 'configurar un temporizador: minutos para el temporizador'."
            ],
            "context": [""]
        },
        {
            "tag": "chistes",
            "patterns": [
                "Cuéntame un chiste",
                "Chiste",
                "Hazme reír"
            ],
            "responses": [
                "Un perfeccionista entró en un bar... al parecer, el bar no estaba lo suficientemente alto.",
                "Comí un reloj ayer, fue muy consumidor de tiempo.",
                "Nunca critiques a alguien hasta que hayas caminado una milla con sus zapatos. De esa manera, cuando los critiques, no podrán escucharte desde tan lejos. Además, tendrás sus zapatos.",
                "El campeón mundial de trabalenguas acaba de ser arrestado. Escuché que le van a dar una sentencia realmente difícil.",
                "Tengo el peor tesauro del mundo. No solo es horrible, sino que es horrible.",
                "¿Qué le dijo el semáforo al coche? 'No mires ahora, me estoy cambiando.'",
                "¿Cómo se llama un muñeco de nieve con bronceado? Un charco.",
                "¿Cómo construye un pingüino una casa? ¡Iglúelo!",
                "Fui a ver al médico por mis problemas de memoria a corto plazo: lo primero que hizo fue hacerme pagar por adelantado.",
                "A medida que envejezco y recuerdo a todas las personas que he perdido en el camino, pienso para mí mismo: tal vez una carrera como guía turístico no era para mí.",
                "Entonces, ¿qué pasa si no sé lo que significa 'Armagedón'? No es el fin del mundo."
            ],
            "context": ["chistes"]
        },
        {
            "tag": "identidad",
            "patterns": [
                "¿Quién eres?",
                "¿Qué eres?"
            ],
            "responses": [
                "Soy Aurora, un Asistente Virtual de aprendizaje profundo."
            ]
        },
        {
            "tag": "fecha_hora",
            "patterns": [
                "¿Qué hora es?",
                "¿Cuál es la fecha?",
                "Fecha",
                "Hora",
                "Dime la fecha",
                "Día",
                "¿Qué día es hoy?"
            ],
            "responses": [
                "Fecha y Hora"
            ]
        },
        {
            "tag": "que_hay",
            "patterns": [
                "¿Qué hay?",
                "¿Qué pasa?",
                "¿Cómo estás?",
                "¿Qué tal?",
                "¿Cómo te va?"
            ],
            "responses": [
                "Todo bien... ¿Y tú?"
            ]
        },
        {
            "tag": "risas",
            "patterns": [
                "jaja",
                "lol",
                "rofl",
                "jajaja",
                "eso es divertido"
            ],
            "responses": [
                "¡Me alegra haberte hecho reír!"
            ]
        },
        {
            "tag": "programador",
            "patterns": [
                "¿Quién te creó?",
                "¿Quién te diseñó?",
                "¿Quién te programó?"
            ],
            "responses": [
                "Fui creada por Los Estudiantes de Funcepal."
            ]
        },
        {
            "tag": "insulto",
            "patterns": [
                "Eres tonta",
                "Cállate",
                "Idiota"
            ],
            "responses": [
                "Bueno, eso duele :("
            ]
        },
        {
            "tag": "actividad",
            "patterns": [
                "¿Qué estás haciendo?",
                "¿En qué estás?",
                "¿Qué haces?"
            ],
            "responses": [
                "¡Hablando contigo, por supuesto!"
            ]
        },
        {
            "tag": "exclamacion",
            "patterns": [
                "Genial",
                "Estupendo",
                "Lo sé",
                "Ok",
                "Sí"
            ],
            "responses": [
                "¡Sí!"
            ]
        },
        {
            "tag": "clima",
            "patterns": [
                "Temperatura",
                "Clima",
                "¿Qué tan caliente está?"
            ],
            "responses": [
                "..."
            ]
        },
        {
            "tag": "Funcepal",
            "patterns": [
                "¿Quién es él?",
                "¿Quién es ese?",
                "¿Quién es Funcepal?",
                "Fundación Centro Educativo Las Palmeras"
            ],
            "responses": [
                "¡Dirígete a cualquiera de sus perfiles sociales para descubrirlo!" 
            ]
        },
        {
            "tag": "contacto",
            "patterns": [
                "Contacta al desarrollador",
                "Contacta a JuanK",
                "Contacta al programador",
                "Contacta al creador"
            ],
            "responses": [
                "Puedes contactar al creador en su"
            ]
        },
        {
            "tag": "aprecio",
            "patterns": [
                "Eres increíble",
                "Eres la mejor",
                "Eres genial",
                "Eres buena"
            ],
            "responses": [
                "¡Gracias!"
            ]
        },
        {
            "tag": "agradable",
            "patterns": [
                "Fue agradable hablar contigo",
                "Buena charla"
            ],
            "responses": [
                "¡Fue agradable hablar contigo también! ¡Vuelve pronto!"
            ]
        },
        {
            "tag": "no",
            "patterns": [
                "No",
                "Nope"
            ],
            "responses": [
                "Ok"
            ]
        },
        {
            "tag": "noticias",
            "patterns": [
                "Noticias",
                "Últimas noticias",
                "Noticias de India"
            ],
            "responses": [
                "..."
            ]
        },
        {
            "tag": "inspiracion",
            "patterns": [
                "¿Quién te inspira?",
                "¿Quién es tu inspiración?",
                "¿Quién te motiva?"
            ],
            "responses": [
                "Personalmente, encuentro a Funcepal muy inspirador. Aunque quizás no sea muy imparcial..."
            ]
        },
        {
            "tag": "cricket",
            "patterns": [
                "Partidos de cricket actuales",
                "Puntuación de cricket"
            ],
            "responses": [
                "..."
            ]
        },
        {
            "tag": "cancion",
            "patterns": [
                "Canciones más populares",
                "Mejores canciones",
                "Canciones populares",
                "Top 10 canciones",
                "Top ten canciones"
            ],
            "responses": [
                "..."
            ]
        },
        {
            "tag": "respuesta_saludo",
            "patterns": [
                "Estoy bien",
                "Estoy bien",
                "Estoy bien",
                "Estoy bien",
                "Bien"
            ],
            "responses": [
                "¡Qué bueno saberlo!"
            ]
        },
        {
            "tag": "temporizador",
            "patterns": [
                "Configurar un temporizador"
            ],
            "responses": [
                "..."
            ]
        },
        {
            "tag": "covid19",
            "patterns": [
                "Covid 19"
            ],
            "responses": [
                "..."
            ]
        },
        {
            "tag": "sugerencia",
            "patterns": [
                "Eres inútil",
                "Inútil",
                "Sugerir",
                "Sugerencias",
                "Eres mala"
            ],
            "responses": [
                "Por favor, envía tus sugerencias por correo electrónico a  ¡Gracias por ayudarme a mejorar!"
            ]
        },
        {
            "tag": "adivinanza",
            "patterns": [
                "Hazme una adivinanza",
                "Hazme una pregunta",
                "Adivinanza"
            ],
            "responses": [
                "¿Qué dos cosas nunca puedes comer para el desayuno?... ¡Almuerzo y cena!",
                "¿Qué palabra está escrita incorrectamente en todos los diccionarios?... Incorrectamente",
                "¿Cómo puede una niña pasar 25 días sin dormir?... ¡Ella duerme por la noche!",
                "¿Cómo haces que el número uno desaparezca?... Agrega la letra G y se vuelve 'gone' (desaparecido)!",
                "¿Qué encontrarás al final de cada arco iris?... La letra 'w' (doble u)",
                "¿Qué se puede atrapar pero nunca lanzar?... Un resfriado",
                "¿Qué tiene un pulgar y cuatro dedos pero no está realmente vivo?... Tus guantes",
                "¿Qué palabra de 5 letras se vuelve más corta cuando le agregas dos letras?... Corta",
                "¿Por qué una bicicleta no puede pararse por sí sola?... ¡Está demasiado cansada!"
            ],
            "context": ["adivinanzas"]
        },
        {
            "tag": "edad",
            "patterns": [
                "¿Cuántos años tienes?",
                "¿Cuándo fuiste creado?",
                "¿Cuál es tu edad?"
            ],
            "responses": [
                "Fui creada en 2023, si eso es lo que estás preguntando."
            ]
        },
    

{
        "tag": "despedida",
        "patterns": [
            "Adiós",
            "Hasta luego",
            "Hasta la próxima",
            "chau",
            "bye",
            "bye bye",
            "Gracias por todo"
        ],
        "responses": [
            "¡Hasta luego, que tengas un buen día!"
        ]
    }
    # Aquí coloca tus intenciones como se definió anteriormente
]

# Función para quitar acentos y caracteres de puntuación
def quitar_acentos_y_puntuacion(texto):
    texto = unidecode.unidecode(texto)  # Elimina acentos
    texto = ''.join(caracter for caracter in texto if caracter not in string.punctuation)  # Elimina signos de puntuación
    return texto

# Función para obtener una respuesta del asistente virtual
def obtener_respuesta(intents, mensaje):
    mensaje = quitar_acentos_y_puntuacion(mensaje.lower())
    
    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in mensaje:
                return random.choice(intent["responses"])

    return "Lo siento, no puedo entenderte. ¿Puedes reformular tu pregunta?"

def permitir_puerto_firewall(puerto):
    try:
        # Agregar una regla de entrada al Firewall de Windows para permitir el tráfico en el puerto especificado
        subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name="Python Port"', 'dir=in', 'action=allow', f'protocol=TCP', f'localport={puerto}'])
        print(f"Regla de Firewall para el puerto {puerto} agregada correctamente.")
    except Exception as e:
        print(f"Error al agregar la regla de Firewall: {str(e)}")

# Ejemplo de uso:
puerto = 5000  # Reemplaza esto con el puerto de tu aplicación Flask
permitir_puerto_firewall(puerto)


@app.route('/chat', methods=['POST'])
def chat():
    if request.method == 'POST':
        user_message = request.json['user_message']
        bot_message = obtener_respuesta(intents, user_message)
        return jsonify({'bot_message': bot_message})


@app.route('/voice', methods=['POST'])
def voice():
    if request.method == 'POST':
        data = request.get_json()
        audio_data = data.get('audio_data')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
