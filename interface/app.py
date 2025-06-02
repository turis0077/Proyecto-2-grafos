# interface/app.py

import solara
from interfaz.login import Login
from interfaz.recomendaciones import Recomendaciones
from interfaz.social import Social

@solara.component
def App():
    # Estado para saber qué pestaña está activa: 0=Login, 1=Recomendaciones, 2=Social
    active_tab, set_active_tab = solara.use_state(0)

    # Opciones de pestañas
    tabs = ["Login / Registro", "Recomendaciones", "Social"]

    return solara.Card(
        [
            solara.Tabs(
                value=active_tab,
                on_change=set_active_tab,
                tabs=tabs,
            ),
            solara.Separator(),
            # Mostrar el componente correspondiente según active_tab
            solara.If(active_tab == 0, Login),
            solara.If(active_tab == 1, Recomendaciones),
            solara.If(active_tab == 2, Social),
        ],
        style={"padding": "1rem", "max-width": "800px", "margin": "auto"},
    )

if __name__ == "__main__":
    solara.render(App)