from typing import List
import streamlit as st
from utils.beam import Beam
from utils.model_cli import ModelCli
from utils.support import Support, SupportTypes
from utils.load import Load, LoadTypes


def add_supports(model_supports: List[dict]):
    assert "beam" in st.session_state
    for support in model_supports:
        st.session_state.beam.add_support(Support(
            position=support["position"],
            category=SupportTypes(support["type"])
        ))
        
    return

def add_loads(loads: List[dict]):
    assert "beam" in st.session_state
    for load in loads:
        st.session_state.beam.add_load(Load(
            magnitude=load["magnitude"],
            category=LoadTypes(load["type"]),
            start=load["start"],
            end=load["end"]
        ))
        
    return    

def main():
    
    st.set_page_config(
        page_title="SMDF - Solid Mechanics",
        page_icon="📊",
    )
    
    st.title("Structural Modeling by Descontinuous Functions")
    
    if "supports" not in st.session_state:
        st.session_state.supports = []
    
    if "loads" not in st.session_state:
        st.session_state.loads = []
    
    st.subheader("Configure Beam")
    with st.form(key="conf_beam"):
        beam_length = st.number_input("Beam Length (m)", format="%f", min_value=0.1, step=0.1)
        beam_height = st.number_input("Beam Height (m)", format="%f", min_value=0.001, step=0.1)
        beam_inertia = st.text_input("Beam Inertia (kN)", value="0.0")
        fixed_beam = st.checkbox("Is beam fixed at position 0.0?", value=True)
        
        beam_submit_button = st.form_submit_button(
            label="Submit",
            on_click=lambda: st.session_state.update({"beam": Beam(h=beam_height, L=beam_length, I=float(beam_inertia))})
        )
        
    if beam_submit_button:
        initial_state = [{"position":0.0, "type":"fixed"}] if fixed_beam else []
        st.session_state.supports = initial_state
        st.success(f"Beam(h={beam_height}, L={beam_length}, I={beam_inertia}) created!")
        with st.expander("Supports"):
            st.json(st.session_state.supports)
    
    
    # Supports
    st.subheader("Configure Beam Supports")
    with st.form(key="conf_supports"):    
        cols_supp = st.columns((2, 2))
        supp_position = cols_supp[0].number_input("Support position", min_value=0.0, max_value=beam_length, 
                                             format="%f", step=0.1)
        supp_category = cols_supp[1].selectbox("Support category", ["fixed", "pinned", "roller"])
        supp_submit_button = st.form_submit_button("Add Support")
        
    if supp_submit_button:
        st.session_state.supports.append({"position":supp_position, "type":supp_category})
        with st.expander("Supports"):
            st.json(st.session_state.supports)
        
    # Loads
    st.subheader("Configure Beam Loads")
    with st.form(key="conf_loads"):
        cols_l1 = st.columns((2, 2))
        magnitude = cols_l1[0].number_input("Load magnitude", format="%f", step=0.1)
        load_category = cols_l1[1].selectbox("Load category", ["centered", "uniformly_distributed", "uniformly_varying"])
        
        st.write(load_category)

        cols_l2 = st.columns((2, 2))
        position_start = cols_l2[0].number_input("Load start", min_value=0.0, max_value=beam_length, format="%f", step=0.1)
        position_end = cols_l2[1].number_input("Load end", min_value=0.0, max_value=beam_length, format="%f", step=0.1)

        load_submit_button = st.form_submit_button("Add Load")
        
    if load_submit_button:
        st.session_state.loads.extend(
            [{"magnitude":magnitude, "type":load_category, "start":position_start, "end":position_end}]
        )
        with st.expander("Loads"):
            st.json(st.session_state.loads)
    

    # Report
    st.subheader("Get Results")
    with st.form(key="report"):
        cols_rep = st.columns((1.5, 1, 1))
        report_submit_button = cols_rep[1].form_submit_button("Generate!")
        
    if not report_submit_button:
        st.stop()
        
    if report_submit_button:
        add_supports(st.session_state.supports)
        add_loads(st.session_state.loads)
        model = ModelCli(st.session_state.beam)
        # is app=True -> mudar diretorios de imagens
            
        with st.spinner("Doing some math..."):
            constants, (x, y), (mesh_x, mesh_y), internal_strain, inertia = model.solve()
            fig = model.plot_results((x, y), (mesh_x, mesh_y), internal_strain, inertia)
        
        with st.expander("Constants"):
            st.json(constants)
        st.pyplot(fig)
            
    # st.stop()
    
if __name__ == "__main__":
    main()