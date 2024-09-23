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

import json
from os.path import dirname
from os.path import join

import streamlit as st
from PIL import Image

# this is to keep the widget values between pages
for k, v in st.session_state.items():
    st.session_state[k] = v

st.set_page_config(page_title="GEMSEO Study", layout="wide")

st.title("GEMSEO Study analysis and prototyping")

logo = Image.open(join(dirname(__file__), "logo-small.png"))
st.image(logo, width=300)

st.markdown(
    """
The GEMSEO Study helps to define the right MDO problem to be
solved before writing any code.

The user only has to define the disciplines by their names,
as well as the input and output names.

Then, the scenario is defined by the names of the objectives, constraints,
design variables, and the selection of the MDO formulation.

The result of the analysis are a N2 and XDSM diagrams.

The N2 (pronounce "N square") diagram represents the coupling between the disciplines, see: [link]({}).

The XDSM (eXtended Design Structure Matrix) diagram represents MDO process.
In particular, it is a standard to represent the MDO formulations, see: [link]({}).
""".format(
        "https://gemseo.readthedocs.io/en/stable/mdo/coupling.html",
        "https://gemseo.readthedocs.io/en/stable/mdo/mdo_formulations.html",
    )
)

st.divider()
st.subheader("Saving and loading a study")
st.markdown(
    """
    You can download the study configuration as a JSON text file and load it in the future.
    """
)
# Handle data saving


uploaded_file = st.file_uploader("Load existing study")
if uploaded_file is not None:
    state = json.loads(uploaded_file.read())
    for k, v in state.items():
        st.session_state[k] = v

download_data = {}


def update_download_data():
    download_data.clear()
    for k, v in st.session_state.items():
        if k.startswith("#"):
            download_data[k] = v


update_download_data()
st.download_button("Save current study", json.dumps(download_data), file_name="gemseo_study.json",
                   on_click=update_download_data)
