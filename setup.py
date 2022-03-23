# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

import rd60xx

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rd60xx",
    version=rd60xx.__version__,
    author="Doridian",
    author_email="git@doridian.net",
    description="Python bindings for RD60XX",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Doridian/rd60xx",
    packages=setuptools.find_packages(),
    install_requires=['PyModbus'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)                                                                                   
