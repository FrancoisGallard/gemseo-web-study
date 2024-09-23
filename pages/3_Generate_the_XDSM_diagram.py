# noqa: D100 putting a string makes ST fail
# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: Francois Gallard
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
from __future__ import annotations

import tempfile
from os.path import join
from typing import TYPE_CHECKING

import streamlit as st
import streamlit.components.v1 as components
from gemseo import MDODiscipline
from gemseo import create_design_space
from gemseo import create_scenario
from gemseo import get_available_formulations

from pages import handle_session_state, create_disciplines, handle_disciplines_summary

if TYPE_CHECKING:
    from gemseo.core.mdo_scenario import MDOScenario

CTYPES = ["inequality", "equality"]


def handle_design_variables() -> None:
    """Handles the design variables."""
    all_inputs = st.session_state["#all_inputs"]
    key = "#Design variables"
    design_variables = st.multiselect(
        "Design variables", options=all_inputs, default=st.session_state.get(key, [])
    )
    st.session_state[key] = design_variables


def handle_formulation() -> None:
    """Handles the MDO formulation."""
    formulations_key = "formulations_list"
    if formulations_key in st.session_state:
        formulations = st.session_state[formulations_key]
    else:
        formulations = get_available_formulations()
        st.session_state[formulations_key] = formulations

    key = "#MDO formulation index"
    index = st.session_state.get(key, formulations.index("MDF"))
    formulation = st.selectbox(
        "MDO Formulation", formulations, index=index, key="MDO formulation"
    )
    st.session_state[key] = formulations.index(formulation)
    st.session_state["#mdo formulation"] = formulation


def handle_objective() -> None:
    """Handles the objective function and its maximization."""
    key = "#objective_index"
    all_outputs = st.session_state["#all_outputs"]
    objective = st.selectbox(
        "Objective function name",
        all_outputs,
        index=st.session_state.get(key, 0),
        key="objective",
    )
    st.session_state[key] = all_outputs.index(objective)
    key = "#maximize_objective"
    maximize_objective = st.checkbox(
        "maximize_objective", value=st.session_state.get(key, False)
    )
    st.session_state[key] = maximize_objective


def handle_constraints() -> None:
    """Handles the constraints definition."""
    key = "#Number of constraints"
    nb_cstr = st.slider(
        "Number of constraints",
        min_value=0,
        max_value=20,
        value=st.session_state.get(key, 0),
        key="Constraints slider",
    )
    st.session_state[key] = nb_cstr

    constraints = {}
    all_outputs = st.session_state["#all_outputs"]
    for i in range(nb_cstr):
        st.divider()
        key = f"#Constraint {i + 1}"
        c_index = st.session_state.get(key)
        constr = st.selectbox(f"Constraint {i + 1}", all_outputs,
                              index=c_index, key="c_" + key)
        if constr is not None:
            st.session_state[key] = all_outputs.index(constr)

        key = f"#constr_type{i}"
        c_type_index = st.session_state.get(key, 0)
        c_type = st.selectbox(
            "Constraint type",
            CTYPES,
            index=c_type_index,
            key="c_" + key,
        )
        if c_type is not None:
            st.session_state[key] = CTYPES.index(c_type)

        if constr:
            constraints[constr] = c_type
    st.session_state["#constraints"] = constraints


def handle_scenario() -> MDOScenario | None:
    """Handles the MDO scenario."""
    design_variables = st.session_state["#Design variables"]
    obj_index = st.session_state["#objective_index"]
    objective = st.session_state["#all_outputs"][obj_index]
    if not (objective and design_variables):
        st.error("Please select an objective and design variables")
    disciplines = st.session_state["disciplines"]
    scenario = None
    if not disciplines:
        st.error("Please select the disciplines.")
    elif st.button("Generate XDSM", type="primary"):
        design_space = create_design_space()
        for name in design_variables:
            design_space.add_variable(name=name)
        try:
            scenario = create_scenario(
                design_space=design_space,
                objective_name=objective,
                maximize_objective=st.session_state["#maximize_objective"],
                disciplines=disciplines,
                formulation=st.session_state["#mdo formulation"],
                grammar_type=MDODiscipline.GrammarType.SIMPLE,
            )
            cmap = {"inequality": "ineq", "equality": "eq"}
            constraints = st.session_state["#constraints"]
            for constr, ctype in constraints.items():
                scenario.add_constraint(constr, constraint_type=cmap[ctype])
        except Exception as err:
            st.error(str(err))  # noqa: G200
            return None
    return scenario


def generate_xdsm(scenario: MDOScenario) -> None:
    """Generates the XDSM diagram."""
    tmpdir = tempfile.mkdtemp()
    scenario.xdsmize(directory_path=tmpdir)
    tmp_html = join(tmpdir, "xdsm.html")
    with open(tmp_html, encoding="utf-8") as html_file:
        source_code = html_file.read()
        st.download_button(
            "Download XDSM standalone HTML file", source_code, file_name="xdsm.html"
        )
        components.html(source_code, width=1280, height=1024)


st.title("XDSM Generation")
handle_session_state()

if "disciplines" not in st.session_state and "#disc_desc" in st.session_state:
    create_disciplines()

# Main display sequence
if "disciplines" in st.session_state:
    st.markdown(
        """
    The XDSM (eXtended Design Structure Matrix) diagram represents MDO process.
    In particular, it is a standard to represent the MDO formulations, see: [link]({}).
    """.format("https://gemseo.readthedocs.io/en/stable/mdo/mdo_formulations.html")
    )
    handle_disciplines_summary()
    st.subheader("Scenario definition")
    handle_design_variables()
    handle_formulation()
    handle_objective()
    handle_constraints()
    scenario = handle_scenario()
    if scenario is not None:
        generate_xdsm(scenario)
else:
    st.error("Disciplines are not ready, please check the Disciplines tab")
