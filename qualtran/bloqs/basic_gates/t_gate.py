#  Copyright 2023 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from functools import cached_property
from typing import Any, Dict, Tuple, TYPE_CHECKING

import attrs
import numpy as np
from attrs import frozen

from qualtran import Bloq, bloq_example, BloqDocSpec, Signature, Soquet, SoquetT
from qualtran.cirq_interop.t_complexity_protocol import TComplexity
from qualtran.drawing import TextBox, WireSymbol

if TYPE_CHECKING:
    import cirq
    import quimb.tensor as qtn

    from qualtran.cirq_interop import CirqQuregT


_TMATRIX = np.array([[1, 0], [0, np.exp(1.0j * np.pi / 4.0)]], dtype=np.complex128)


@frozen
class TGate(Bloq):
    r"""The T gate.

    This is the fourth root of the Pauli Z gate. Quantum programs composed solely
    of gates belonging to the Clifford group (like X, Z, Hadamard, CNOT, S) can be simulated
    efficiently by a classical computer and therefore offer no quantum advantage. The Clifford
    gates do not provide a universal quantum gateset. The addition of any non-Clifford gate
    makes the gateset universal. One of the most popular additions is the T gate, yielding
    the common Clifford+T gateset.

    The unitary matrix of `cirq.T` is
    $$
    \begin{bmatrix}
        1 & 0 \\
        0 & e^{i \pi /4}
    \end{bmatrix}
    $$

    Args:
        is_adjoint: If True, this bloq is $T^\dagger$ instead.

    Registers:
        q: The qubit

    References:
        [Universal Quantum Computation with ideal Clifford gates and noisy ancillas](https://arxiv.org/abs/quant-ph/0403025).
        Bravyi and Kitaev. 2004.

        [Fast and efficient exact synthesis of single qubit unitaries generated by Clifford and T gates](https://arxiv.org/abs/1206.5236).
        Kliuchnikov et. al. 2012.

        [Universal Gate Set, Magic States, and costliness of the T gate](https://quantumcomputing.stackexchange.com/a/33358).
        Gidney. 2023.
    """

    is_adjoint: bool = False

    @cached_property
    def signature(self) -> 'Signature':
        return Signature.build(q=1)

    def _t_complexity_(self) -> 'TComplexity':
        return TComplexity(t=1)

    def add_my_tensors(
        self,
        tn: 'qtn.TensorNetwork',
        tag: Any,
        *,
        incoming: Dict[str, 'SoquetT'],
        outgoing: Dict[str, 'SoquetT'],
    ):
        import quimb.tensor as qtn

        data = _TMATRIX.conj().T if self.is_adjoint else _TMATRIX
        tn.add(
            qtn.Tensor(
                data=data, inds=(outgoing['q'], incoming['q']), tags=[self.short_name(), tag]
            )
        )

    def adjoint(self) -> 'Bloq':
        return attrs.evolve(self, is_adjoint=not self.is_adjoint)

    def as_cirq_op(
        self, qubit_manager: 'cirq.QubitManager', q: 'CirqQuregT'
    ) -> Tuple['cirq.Operation', Dict[str, 'CirqQuregT']]:
        import cirq

        (q,) = q
        return cirq.T(q), {'q': np.array([q])}

    def pretty_name(self) -> str:
        maybe_dag = '†' if self.is_adjoint else ''
        return f'T{maybe_dag}'

    def __str__(self):
        maybe_dag = 'is_adjoint=True' if self.is_adjoint else ''
        return f'TGate({maybe_dag})'

    def wire_symbol(self, soq: 'Soquet') -> 'WireSymbol':
        return TextBox(self.pretty_name())


@bloq_example
def _t_gate() -> TGate:
    t_gate = TGate()
    return t_gate


_T_GATE_DOC = BloqDocSpec(
    bloq_cls=TGate, import_line='from qualtran.bloqs.basic_gates import TGate', examples=[_t_gate]
)
