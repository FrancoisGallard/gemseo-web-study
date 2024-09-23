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
"""A web GUI for GEMSEO study."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from gemseo.core.discipline import MDODiscipline
from gemseo.problems.scalable.linear.disciplines_generator import create_disciplines_from_desc


def handle_session_state():
    """
    Handles the session state to allow it to be passed between the pages.
    This is a known and dirty workaround in streamlit.
    """
    # this is to keep the widget values between pages
    for k, v in st.session_state.items():
        if k.startswith('#'):
            st.session_state[k] = v


@st.cache_data
def create_mdo_disciplines(disc_desc) -> list[MDODiscipline]:
    """Creates the disciplines instances.

    Returns:
        The list of disciplines
    """
    disciplines = create_disciplines_from_desc(
        disc_desc, grammar_type=MDODiscipline.GrammarType.SIMPLE
    )
    st.session_state["disciplines"] = disciplines
    return disciplines


def create_disciplines() -> None:
    """
    Creates the disciplines from the #disc_desc list in the session state.
    """
    disc_desc = st.session_state.get("#disc_desc")
    try:
        if disc_desc is not None:
            disciplines = create_mdo_disciplines(disc_desc)
            st.session_state["disciplines"] = disciplines

    except (ValueError, TypeError):
        if "disciplines" in st.session_state:
            del st.session_state["disciplines"]


def handle_disciplines_summary() -> None:
    """Generates a summary of the disciplines Uses a Dataframe view widget.
    """
    st.divider()
    st.subheader("Disciplines summary")
    disc_desc = st.session_state.get("#disc_desc")
    try:
        if disc_desc is not None:
            df = pd.DataFrame.from_records(
                [
                    {
                        "Name": i[0],
                        "Inputs": str(sorted(i[1])),
                        "Outputs": str(sorted(i[2])),
                    }
                    for i in disc_desc
                ],
                columns=["Name", "Inputs", "Outputs"],
            )
            st.dataframe(df, hide_index=True)
            st.session_state["disciplines_dataframe"] = df
            st.divider()


    except (ValueError, TypeError):
        if "disciplines" in st.session_state:
            del st.session_state["disciplines"]
