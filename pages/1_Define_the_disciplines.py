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

import pandas as pd
import streamlit as st
from gemseo import MDODiscipline
from gemseo.problems.scalable.linear.disciplines_generator import (
    create_disciplines_from_desc,
)
from streamlit_tags import st_tags

# this is to keep the widget values between pages
for k, v in st.session_state.items():
    if k.startswith('#'):
        st.session_state[k] = v


def handle_disciplines_number() -> int:
    """Handle the widget that defines the number of disciplines.

    Stores the
    """
    key = "#Number of disciplines"
    key_val = key + "_val"
    value = st.session_state.get(key_val, 2)
    value = st.slider(
        "The number of disciplines", min_value=1, max_value=20, value=value)
    st.session_state[key_val] = value


def handle_disciplines_description() -> None:
    """Handles the disciplines description.

    For each discipline, of number nb_disc,
    creates the widgets that allow the user to fill the inputs, outputs,
    and discipline name.

    """
    disc_desc = []
    nb_disc = st.session_state["#Number of disciplines_val"]
    for i in range(nb_disc):
        st.divider()
        key = f"#Disc_{i}_name"
        value = st.session_state.get(key, f"Discipline_{i}")
        name = st.text_input("Discipline Name", value=value, key=f"Disc_{i}_name")
        st.session_state[key] = name

        key = f"#Disc_inputs_{i}"
        value = st.session_state.get(key, [])
        inputs = st_tags(
            label=f"Discipline {i} Inputs:",
            text="Press enter to add more",
            value=value,
            key=key,
        )

        key = f"#Disc_outputs_{i}"
        value = st.session_state.get(key, [])
        outputs = st_tags(
            label=f"Discipline {i} Outputs:",
            text="Press enter to add more",
            value=value,
            key=key,
        )
        if inputs and outputs:
            disc_desc.append((name, tuple(inputs), tuple(outputs)))
    st.session_state["#disc_desc"] = tuple(disc_desc)


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

            all_outputs = set()
            all_inputs = set()
            for disc in disciplines:
                all_outputs.update(disc.get_output_data_names())
                all_inputs.update(disc.get_input_data_names())
            st.session_state["#all_outputs"] = sorted(all_outputs)
            st.session_state["#all_inputs"] = sorted(all_inputs)

    except (ValueError, TypeError):
        if "disciplines" in st.session_state:
            del st.session_state["disciplines"]


def handle_disciplines_summary() -> None:
    """Generates a summary of the disciplines Uses a Dataframe view widget.

    Args:
        disc_desc: The disciplines description.
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


# Main display sequence
handle_disciplines_number()
handle_disciplines_description()
create_disciplines()
handle_disciplines_summary()
