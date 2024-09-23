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

import streamlit as st
from streamlit_tags import st_tags

from pages import handle_session_state, create_disciplines, handle_disciplines_summary


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
def get_all_ios(disc_desc):
    all_outputs = set()
    all_inputs = set()
    for _, input_names, output_names in disc_desc:
        all_inputs.update(input_names)
        all_outputs.update(output_names)

    return sorted(all_inputs), sorted(all_outputs)


def handle_all_ios():
    disc_desc = st.session_state.get("#disc_desc")
    if disc_desc is not None:
        all_inputs, all_outputs = get_all_ios(disc_desc)
        st.session_state["#all_outputs"] = all_outputs
        st.session_state["#all_inputs"] = all_inputs


# Main display sequence
handle_session_state()
st.title("Disciplines defintion")
handle_disciplines_number()
handle_disciplines_description()
create_disciplines()
handle_all_ios()
handle_disciplines_summary()
