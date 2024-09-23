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

import streamlit as st
import streamlit.components.v1 as components
from gemseo import MDODiscipline
from gemseo.core.coupling_structure import MDOCouplingStructure
from gemseo.problems.scalable.linear.disciplines_generator import create_disciplines_from_desc
from matplotlib.pyplot import gcf

from pages import handle_session_state


@st.cache_data
def create_mdo_disciplines(disc_desc) -> list[MDODiscipline]:
    """Creates the disciplines instances."""

    disciplines = create_disciplines_from_desc(
        disc_desc, grammar_type=MDODiscipline.GrammarType.SIMPLE
    )
    st.session_state["disciplines"] = disciplines
    return disciplines


def create_disciplines() -> None:
    disc_desc = st.session_state.get("#disc_desc")
    try:
        if disc_desc is not None:
            disciplines = create_mdo_disciplines(disc_desc)
            st.session_state["disciplines"] = disciplines

    except (ValueError, TypeError):
        if "disciplines" in st.session_state:
            del st.session_state["disciplines"]


def generate_html(coupling_structure) -> str:
    """Generates the HTML file.

    Args:
        _disciplines: The disciplines instances.
        disc_desc: The disciplines descriptions.
    """
    tmpdir = tempfile.mkdtemp()
    tmp_file = join(tmpdir, "n2.png")
    tmp_html = join(tmpdir, "n2.html")

    coupling_structure.plot_n2_chart(file_path=tmp_file, show_data_names=True,
                                     save=True, show=False, show_html=False
                                     )
    with open(tmp_html, encoding="utf-8") as html_file:  #
        return html_file.read()


@st.cache_data
def create_coupling_structure(disc_desc: list) -> MDOCouplingStructure:
    """Generates the HTML file.

    Args:
        _disciplines: The disciplines instances.
        disc_desc: The disciplines descriptions.
    """
    disciplines = st.session_state["disciplines"]
    return MDOCouplingStructure(disciplines)


def handle_n2_genration() -> None:
    """Handles the generation of the N2.

    From the disciplines tab, creates an N2 diagram in the page if the inputs are ready.
    """
    if "disciplines" in st.session_state:
        disciplines = st.session_state["disciplines"]
        format = st.selectbox(
            "N2 diagram format", ["HTML", "basic"], index=1, key="N2 diagram format"
        )
        disc_desc = st.session_state["#disc_desc"]
        coupling_structure = create_coupling_structure(disc_desc)
        if format == "HTML" and st.button("Generate N2", type="primary"):

            source_code = generate_html(coupling_structure)
            st.download_button(
                "Download N2 standalone HTML file", source_code, file_name="N2.html"
            )
            components.html(source_code, width=800, height=800)
        else:
            coupling_structure._MDOCouplingStructure__draw_n2_chart(
                file_path="", show_data_names=True, save=False, show=False,
                fig_size=(8, 8))

            st.pyplot(gcf())

    else:
        st.error("Disciplines are not ready, please check the Disciplines tab.")


# this is to keep the widget values between pages
handle_session_state()
st.title("N2 diagram generation")
# Main display sequence
st.markdown(
    """
The N2 (pronounce "N square") diagram represents the coupling between the disciplines, see: [link]({}).
""".format("https://gemseo.readthedocs.io/en/stable/mdo/coupling.html")
)

if "disciplines" not in st.session_state and "#disc_desc" in st.session_state:
    create_disciplines()
handle_n2_genration()
