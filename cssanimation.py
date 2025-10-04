import streamlit as st

st.set_page_config(page_title="Animated Background", layout="wide")

# Inject working CSS
st.markdown("""
    <style>
    /* Gradient animation keyframes */
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Apply to the main container */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #a18cd1, #fbc2eb);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        height: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌈 Animated Gradient Background")
st.write("Now the animated gradient works in latest Streamlit.")


#------------------------------------------------------------------------
# import streamlit as st

# st.set_page_config(page_title="GIF Background", layout="wide")

# st.markdown("""
#     <style>
#     .stApp {
#         background: url("https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif");
#         background-size: cover;
#         background-repeat: no-repeat;
#         background-attachment: fixed;
#     }
#     </style>
# """, unsafe_allow_html=True)

# st.title("🎞️ GIF Background in Streamlit")
# st.write("Using a looping GIF as background.")

#----------------------------------------------------------------------

# import streamlit as st

# st.set_page_config(page_title="Particles Background", layout="wide")

# st.markdown("""
#     <script src="https://cdn.jsdelivr.net/npm/particles.js"></script>
#     <div id="particles-js"></div>

#     <style>
#     #particles-js {
#         position: fixed;
#         width: 100%;
#         height: 100%;
#         z-index: -1;
#         top: 0;
#         left: 0;
#     }
#     </style>

#     <script>
#     particlesJS("particles-js", {
#         "particles": {
#             "number": {"value": 80},
#             "size": {"value": 3},
#             "move": {"speed": 2},
#             "line_linked": {"enable": true},
#             "opacity": {"value": 0.5}
#         }
#     });
#     </script>
# """, unsafe_allow_html=True)

# st.title("✨ Particle Background in Streamlit")
# st.write("This uses particles.js for an interactive animated effect.")

