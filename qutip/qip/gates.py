# This file is part of QuTiP: Quantum Toolbox in Python.
#
#    Copyright (c) 2011 and later, Paul D. Nation and Robert J. Johansson.
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are
#    met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of the QuTiP: Quantum Toolbox in Python nor the names
#       of its contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#    PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#    HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################

from numpy import sqrt, array, exp, where, prod
import scipy.sparse as sp
from qutip.states import (basis, qstate, state_number_index,
                          state_number_enumerate)
from qutip.qobj import Qobj
from qutip.operators import *
from qutip.tensor import tensor
from qutip.states import fock_dm


def rotation(op, phi, N=None, target=0):
    """Single-qubit rotation for operator op with angle phi.

    Returns
    -------
    result : qobj
        Quantum object for operator describing the rotation.
    """
    if not N is None:
        return gate_expand_1toN(rotation(op, phi), N, target)
    else:
        return (-1j * op * phi / 2).expm()


def cphase(theta, N=2, control=0, target=1):
    """
    Returns quantum object representing the phase shift gate.

    Parameters
    ----------
    theta : float
        Phase rotation angle.

    N : integer
        The number of qubits in the target space.

    control : integer
        The index of the control qubit.

    target : integer
        The index of the target qubit.

    Returns
    -------
    U : qobj
        Quantum object representation of controlled phase gate.
    """

    if N < 1 or target < 0 or control < 0:
        raise ValueError("Minimum value: N=1, control=0 and target=0")

    if control >= N or target >= N:
        raise ValueError("control and target need to be smaller than N")

    U_list1 = [identity(2)] * N
    U_list2 = [identity(2)] * N

    U_list1[control] = fock_dm(2, 1)
    U_list1[target] = phasegate(theta)

    U_list2[control] = fock_dm(2, 0)

    U = tensor(U_list1) + tensor(U_list2)
    return U


def rx(phi, N=None, target=0):
    """Single-qubit rotation for operator sigmax with angle phi.

    Returns
    -------
    result : qobj
        Quantum object for operator describing the rotation.

    """
    if not N is None:
        return gate_expand_1toN(rx(phi), N, target)
    else:
        return Qobj([[np.cos(phi / 2), -1j * np.sin(phi / 2)],
                     [-1j * np.sin(phi / 2), np.cos(phi / 2)]])


def ry(phi, N=None, target=0):
    """Single-qubit rotation for operator sigmay with angle phi.

    Returns
    -------
    result : qobj
        Quantum object for operator describing the rotation.

    """
    if not N is None:
        return gate_expand_1toN(ry(phi), N, target)
    else:
        return Qobj([[np.cos(phi / 2), -np.sin(phi / 2)],
                     [np.sin(phi / 2), np.cos(phi / 2)]])


def rz(phi, N=None, target=0):
    """Single-qubit rotation for operator sigmaz with angle phi.

    Returns
    -------
    result : qobj
        Quantum object for operator describing the rotation.

    """
    if not N is None:
        return gate_expand_1toN(rz(phi), N, target)
    else:
        return Qobj([[np.exp(-1j * phi / 2), 0],
                     [0, np.exp(1j * phi / 2)]])


def controlled_gate(U, N=2, control=0, target=1, control_value=1):
    """
    Create an N-qubit controlled gate from a single-qubit gate U with the given
    control and target qubits.

    Parameters
    ----------
    U : Qobj
        Arbitrary single-qubit gate.

    N : integer
        The number of qubits in the target space.

    control : integer
        The index of the first control qubit.

    target : integer
        The index of the target qubit.

    control_value : integer (1)
        The state of the control qubit that activates the gate U.

    Returns
    -------
    result : qobj
        Quantum object representing the controlled-U gate.
    """

    if [N, control, target] == [2, 0, 1]:
        return (tensor(fock_dm(2, control_value), U) +
                tensor(fock_dm(2, 1 - control_value), identity(2)))
    else:
        U2 = controlled_gate(U, control_value=control_value)
        return gate_expand_2toN(U2, N=N, control=control, target=target)


def cnot(N=None, control=0, target=1):
    """
    Quantum object representing the CNOT gate.

    Returns
    -------
    cnot_gate : qobj
        Quantum object representation of CNOT gate

    Examples
    --------
    >>> cnot()
    Quantum object: dims = [[2, 2], [2, 2]], \
shape = [4, 4], type = oper, isHerm = True
    Qobj data =
        [[ 1.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  1.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  1.+0.j]
         [ 0.+0.j  0.+0.j  1.+0.j  0.+0.j]]

    """
    if (control == 1 and target == 0) and N is None:
        N = 2

    if not N is None:
        return gate_expand_2toN(cnot(), N, control, target)
    else:
        return Qobj([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 0, 1],
                     [0, 0, 1, 0]],
                    dims=[[2, 2], [2, 2]])


def csign(N=None, control=0, target=1):
    """
    Quantum object representing the CSIGN gate.

    Returns
    -------
    csign_gate : qobj
        Quantum object representation of CSIGN gate

    Examples
    --------
    >>> csign()
    Quantum object: dims = [[2, 2], [2, 2]], \
shape = [4, 4], type = oper, isHerm = True
    Qobj data =
        [[ 1.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  1.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  1.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  -1.+0.j]]

    """
    if (control == 1 and target == 0) and N is None:
        N = 2
        
    if not N is None:
        return gate_expand_2toN(csign(), N, control, target)
    else:
        return Qobj([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, -1]],
                    dims=[[2, 2], [2, 2]])


def berkeley(N=None, targets=[0, 1]):
    """
    Quantum object representing the Berkeley gate.
    berkeley()
    Quantum object: dims = [[2, 2], [2, 2]], \
shape = [4, 4], type = oper, isHerm = True
    Qobj data =
        [[ cos(pi/8).+0.j  0.+0.j           0.+0.j           0.+sin(pi/8).j]
         [ 0.+0.j          cos(3pi/8).+0.j  0.+sin(3pi/8).j  0.+0.j]
         [ 0.+0.j          0.+sin(3pi/8).j  cos(3pi/8).+0.j  0.+0.j]
         [ 0.+sin(pi/8).j  0.+0.j           0.+0.j           cos(pi/8).+0.j]]

    Returns
    -------
    berkeley_gate : qobj
        Quantum object representation of Berkeley gate

    """
    if (targets[0] == 1 and targets[1] == 0) and N is None:
        N = 2
        
    if not N is None:
        return gate_expand_2toN(cnot(), N, targets=targets)
    else:
        return Qobj([[np.cos(np.pi/8), 0, 0, 1.0j * np.sin(np.pi/8)],
                     [0, np.cos(3*np.pi/8), 1.0j * np.sin(3*np.pi/8), 0],
                     [0, 1.0j * np.sin(3*np.pi/8), np.cos(3*np.pi/8), 0],
                     [1.0j * np.sin(np.pi/8), 0, 0, np.cos(np.pi/8)]],
                    dims=[[2, 2], [2, 2]])


def swapalpha(alpha, N=None, targets=[0, 1]):
    """
    Quantum object representing the SWAPalpha gate.
    swapalpha(alpha)
    Quantum object: dims = [[2, 2], [2, 2]], \
shape = [4, 4], type = oper, isHerm = True
    Qobj data =
        [[ 1.+0.j  0.+0.j                    0.+0.j                    0.+0.j]
         [ 0.+0.j  0.5*(1 + exp(j*pi*alpha)  0.5*(1 - exp(j*pi*alpha)  0.+0.j]
         [ 0.+0.j  0.5*(1 - exp(j*pi*alpha)  0.5*(1 + exp(j*pi*alpha)  0.+0.j]
         [ 0.+0.j  0.+0.j                    0.+0.j                    1.+0.j]]

    Returns
    -------
    swapalpha_gate : qobj
        Quantum object representation of SWAPalpha gate

    """
    if (targets[0] == 1 and targets[1] == 0) and N is None:
        N = 2
        
    if not N is None:
        return gate_expand_2toN(cnot(), N, targets=targets)
    else:
        return Qobj([[1, 0, 0, 0],
                     [0, 0.5 * (1 + np.exp(1.0j*np.pi*alpha)),
                      0.5 * (1 - np.exp(1.0j*np.pi*alpha)), 0],
                     [0, 0.5 * (1 - np.exp(1.0j*np.pi*alpha)),
                      0.5 * (1 + np.exp(1.0j*np.pi*alpha)), 0],
                     [0, 0, 0, 1]],
                    dims=[[2, 2], [2, 2]])


def fredkin(N=None, control=0, targets=[1, 2]):
    """Quantum object representing the Fredkin gate.

    Returns
    -------
    fredkin_gate : qobj
        Quantum object representation of Fredkin gate.

    Examples
    --------
    >>> fredkin()
    Quantum object: dims = [[2, 2, 2], [2, 2, 2]], \
shape = [8, 8], type = oper, isHerm = True
    Qobj data =
        [[ 1.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  1.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  1.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  1.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  0.+0.j  1.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  1.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  1.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  1.+0.j]]

    """
    if [control, targets[0], targets[1]] != [0, 1, 2] and N is None:
        N = 3

    if not N is None:
        return gate_expand_3toN(fredkin(), N, [control, targets[0]], targets[1])

    else:
        return Qobj([[1, 0, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 0, 0],
                     [0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 1, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 1]],
                    dims=[[2, 2, 2], [2, 2, 2]])
        

def toffoli(N=None, controls=[0, 1], target=2):
    """Quantum object representing the Toffoli gate.

    Returns
    -------
    toff_gate : qobj
        Quantum object representation of Toffoli gate.

    Examples
    --------
    >>> toffoli()
    Quantum object: dims = [[2, 2, 2], [2, 2, 2]], \
shape = [8, 8], type = oper, isHerm = True
    Qobj data =
        [[ 1.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  1.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  1.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  1.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  0.+0.j  1.+0.j  0.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  1.+0.j  0.+0.j  0.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  1.+0.j]
         [ 0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  0.+0.j  1.+0.j  0.+0.j]]


    """
    if [controls[0], controls[1], target] != [0, 1, 2] and N is None:
        N = 3

    if not N is None:
        return gate_expand_3toN(toffoli(), N, controls, target)

    else:
        return Qobj([[1, 0, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 0, 0],
                     [0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 0, 0, 0, 1, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 1],
                     [0, 0, 0, 0, 0, 0, 1, 0]],
                    dims=[[2, 2, 2], [2, 2, 2]])


def swap(N=None, targets=[0 ,1]):
    """Quantum object representing the SWAP gate.

    Returns
    -------
    swap_gate : qobj
        Quantum object representation of SWAP gate

    Examples
    --------
    >>> swap()
    Quantum object: dims = [[2, 2], [2, 2]], \
shape = [4, 4], type = oper, isHerm = True
    Qobj data =
    [[ 1.+0.j  0.+0.j  0.+0.j  0.+0.j]
     [ 0.+0.j  0.+0.j  1.+0.j  0.+0.j]
     [ 0.+0.j  1.+0.j  0.+0.j  0.+0.j]
     [ 0.+0.j  0.+0.j  0.+0.j  1.+0.j]]

    """
    if targets != [0, 1] and N is None:
        N = 2

    if not N is None:
        return gate_expand_2toN(swap(), N, targets=targets)

    else:
        return Qobj([[1, 0, 0, 0],
                     [0, 0, 1, 0],
                     [0, 1, 0, 0],
                     [0, 0, 0, 1]],
                    dims=[[2, 2], [2, 2]])


def iswap(N=None, targets=[0, 1]):
    """Quantum object representing the iSWAP gate.

    Returns
    -------
    iswap_gate : qobj
        Quantum object representation of iSWAP gate

    Examples
    --------
    >>> iswap()
    Quantum object: dims = [[2, 2], [2, 2]], \
shape = [4, 4], type = oper, isHerm = False
    Qobj data =
    [[ 1.+0.j  0.+0.j  0.+0.j  0.+0.j]
     [ 0.+0.j  0.+0.j  0.+1.j  0.+0.j]
     [ 0.+0.j  0.+1.j  0.+0.j  0.+0.j]
     [ 0.+0.j  0.+0.j  0.+0.j  1.+0.j]]
    """
    if targets != [0, 1] and N is None:
        N = 2

    if not N is None:
        return gate_expand_2toN(iswap(), N, targets=targets)

    else:
        return Qobj([[1, 0, 0, 0],
                     [0, 0, 1j, 0],
                     [0, 1j, 0, 0],
                     [0, 0, 0, 1]],
                    dims=[[2, 2], [2, 2]])


def sqrtiswap(N=None, targets=[0, 1]):
    """Quantum object representing the square root iSWAP gate.

    Returns
    -------
    sqrtiswap_gate : qobj
        Quantum object representation of square root iSWAP gate

    Examples
    --------
    >>> sqrtiswap()
    Quantum object: dims = [[2, 2], [2, 2]], \
shape = [4, 4], type = oper, isHerm = False
    Qobj data =
    [[ 1.00000000+0.j   0.00000000+0.j   \
       0.00000000+0.j          0.00000000+0.j]
     [ 0.00000000+0.j   0.70710678+0.j   \
       0.00000000-0.70710678j  0.00000000+0.j]
     [ 0.00000000+0.j   0.00000000-0.70710678j\
  0.70710678+0.j          0.00000000+0.j]
     [ 0.00000000+0.j   0.00000000+0.j   \
       0.00000000+0.j          1.00000000+0.j]]
    """
    if targets != [0, 1] and N is None:
        N = 2

    if not N is None:
        return gate_expand_2toN(sqrtiswap(), N, targets=targets)
    else:
        return Qobj(array([[1, 0, 0, 0],
                           [0, 1 / sqrt(2), 1j / sqrt(2), 0],
                           [0, 1j / sqrt(2), 1 / sqrt(2), 0],
                           [0, 0, 0, 1]]), dims=[[2, 2], [2, 2]])


def sqrtswap(N=None, targets=[0, 1]):
    """Quantum object representing the square root SWAP gate.

    Returns
    -------
    sqrtswap_gate : qobj
        Quantum object representation of square root SWAP gate

    """
    if targets != [0, 1] and N is None:
        N = 2

    if not N is None:
        return gate_expand_2toN(sqrtswap(), N, targets=targets)
    else:
        return Qobj(array([[1, 0, 0, 0],
                           [0, 0.5 + 0.5j, 0.5 - 0.5j, 0],
                           [0, 0.5 - 0.5j, 0.5 + 0.5j, 0],
                           [0, 0, 0, 1]]),
                    dims=[[2, 2], [2, 2]])


def sqrtnot(N=None, target=0):
    """Single-qubit square root NOT gate.

    Returns
    -------
    result : qobj
        Quantum object for operator describing the square root NOT gate.

    """
    if not N is None:
        return gate_expand_1toN(sqrtnot(), N, target)
    else:
        return Qobj([[0.5 + 0.5j, 0.5 - 0.5j],
                     [0.5 - 0.5j, 0.5 + 0.5j]])


def snot(N=None, target=0):
    """Quantum object representing the SNOT (Hadamard) gate.

    Returns
    -------
    snot_gate : qobj
        Quantum object representation of SNOT gate.

    Examples
    --------
    >>> snot()
    Quantum object: dims = [[2], [2]], \
shape = [2, 2], type = oper, isHerm = True
    Qobj data =
    [[ 0.70710678+0.j  0.70710678+0.j]
     [ 0.70710678+0.j -0.70710678+0.j]]

    """
    if not N is None:
        return gate_expand_1toN(snot(), N, target)
    else:
        return 1/sqrt(2.0) * Qobj([[1,1],
                                   [1,-1]])


def _hamming_distance(x, bits=32):
    """
    Calculate the bit-wise Hamming distance of x from 0: That is, the number
    1s in the integer x.
    """
    tot = 0
    while x:
        tot += 1
        x &= x - 1
    return tot


def hadamard_transform(N=1):
    """Quantum object representing the N-qubit Hadamard gate.

    Returns
    -------
    q : qobj
        Quantum object representation of the N-qubit Hadamard gate.
    """
    data = 2 ** (-N / 2) * np.array([[(-1) ** _hamming_distance(i & j)
                                      for i in range(2 ** N)]
                                     for j in range(2 ** N)])

    return Qobj(data, dims=[[2] * N, [2] * N])


def phasegate(theta, N=None, target=0):
    """
    Returns quantum object representing the phase shift gate.

    Parameters
    ----------
    theta : float
        Phase rotation angle.

    Returns
    -------
    phase_gate : qobj
        Quantum object representation of phase shift gate.

    Examples
    --------
    >>> phasegate(pi/4)
    Quantum object: dims = [[2], [2]], \
shape = [2, 2], type = oper, isHerm = False
    Qobj data =
    [[ 1.00000000+0.j          0.00000000+0.j        ]
     [ 0.00000000+0.j          0.70710678+0.70710678j]]

    """
    if not N is None:
        return gate_expand_1toN(phasegate(theta), N, target)
    else:
        return Qobj([[1, 0],
                     [0, np.exp(1.0j * theta)]],
                    dims=[[2], [2]])

def globalphase(theta, N=1):
    """
    Returns quantum object representing the global phase shift gate.

    Parameters
    ----------
    theta : float
        Phase rotation angle.

    Returns
    -------
    phase_gate : qobj
        Quantum object representation of global phase shift gate.

    Examples
    --------
    >>> phasegate(pi/4)
    Quantum object: dims = [[2], [2]], \
shape = [2, 2], type = oper, isHerm = False
    Qobj data =
    [[ 0.70710678+0.70710678j          0.00000000+0.j]
     [ 0.00000000+0.j          0.70710678+0.70710678j]]

    """
    data = (np.exp(1.0j * theta) 
            * sp.eye(2**N, 2**N, dtype=complex, format="csr")) 
    return Qobj(data, dims=[[2] * N, [2] * N])



def gate_sequence_product(U_list, left_to_right=True):
    """
    Calculate the overall unitary matrix for a given list of unitary operations 
    
    Parameters
    ----------
    U_list : list
        List of gates implementing the quantum circuit.
    
    left_to_right: Boolean
        Check if multiplication is to be done from left to right.

    Returns
    -------
    U_overall: qobj
        Overall unitary matrix of a given quantum circuit.

    """
    U_overall = 1
    for U in U_list:
        if left_to_right:
            U_overall = U * U_overall 
        else:
            U_overall = U_overall * U

    return U_overall        
        

def gate_expand_1toN(U, N, target):
    """
    Create a Qobj representing a one-qubit gate that act on a system with N
    qubits.

    Parameters
    ----------
    U : Qobj
        The one-qubit gate

    N : integer
        The number of qubits in the target space.

    target : integer
        The index of the target qubit.

    Returns
    -------
    gate : qobj
        Quantum object representation of N-qubit gate.
    """

    if N < 1:
        raise ValueError("integer N must be larger or equal to 1")

    if target >= N:
        raise ValueError("target must be integer < integer N")

    return tensor([identity(2)] * (target) + [U] +
                  [identity(2)] * (N - target - 1))


def gate_expand_2toN(U, N, control=None, target=None, targets=None):
    """
    Create a Qobj representing a two-qubit gate that act on a system with N
    qubits.

    Parameters
    ----------
    U : Qobj
        The two-qubit gate

    N : integer
        The number of qubits in the target space.

    control : integer
        The index of the control qubit.

    target : integer
        The index of the target qubit.

    targets : list
        List of target qubits.

    Returns
    -------
    gate : qobj
        Quantum object representation of N-qubit gate.
    """

    if targets is not None:
        control, target = targets

    if control is None or target is None:
        raise ValueError("Specify value of control and target")

    if N < 2:
        raise ValueError("integer N must be larger or equal to 2")

    if control >= N or target >= N:
        raise ValueError("control and not target must be integer < integer N")

    if control == target:
        raise ValueError("target and not control cannot be equal")

    p = list(range(N))

    if target == 0 and control == 1:
        p[control], p[target] = p[target], p[control]

    elif target == 0:
        p[1], p[target] = p[target], p[1]
        p[1], p[control] = p[control], p[1]

    else:
        p[1], p[target] = p[target], p[1]
        p[0], p[control] = p[control], p[0]

    return tensor([U] + [identity(2)] * (N - 2)).permute(p)


def gate_expand_3toN(U, N, controls=[0, 1], target=2):
    """
    Create a Qobj representing a three-qubit gate that act on a system with N
    qubits.

    Parameters
    ----------
    U : Qobj
        The three-qubit gate

    N : integer
        The number of qubits in the target space.

    controls : list
        The list of the control qubits.

    target : integer
        The index of the target qubit.

    Returns
    -------
    gate : qobj
        Quantum object representation of N-qubit gate.
    """

    if N < 3:
        raise ValueError("integer N must be larger or equal to 3")

    if controls[0] >= N or controls[1] >= N or target >= N:
        raise ValueError(
            "control and not target is None must be integer < integer N")

    if (controls[0] == target or controls[1] == target 
        or controls[0] == controls[1]):
        raise ValueError("controls[0], controls[1], and target cannot be equal")

    p = list(range(N))
    p1 = list(range(N))
    p2 = list(range(N))

    if controls[0] <= 2 and controls[1] <= 2 and target <= 2:
        p[0], p[controls[0]] = p[controls[0]], p[0]
        p1[1], p1[controls[1]] = p1[controls[1]], p1[1]
        p2[2], p2[target] = p2[target], p2[2]
        p = [p[p1[p2[k]]] for k in range(N)]

    #
    # N >= 3 cases
    #

    elif controls[0] == 0 and controls[1] == 1:
        p[2], p[target] = p[target], p[2]

    elif controls[0] == 0 and target == 2:
        p[1], p[controls[1]] = p[controls[1]], p[1]

    elif controls[1] == 1 and target == 2:
        p[0], p[controls[0]] = p[controls[0]], p[0]

    elif controls[0] == 1 and controls[1] == 0:
        p[controls[1]], p[controls[0]] = p[controls[0]], p[controls[1]]
        p2[2], p2[target] = p2[target], p2[2]
        p = [p2[p[k]] for k in range(N)]

    elif controls[0] == 2 and target == 0:
        p[target], p[controls[0]] = p[controls[0]], p[target]
        p1[1], p1[controls[1]] = p1[controls[1]], p1[1]
        p = [p1[p[k]] for k in range(N)]

    elif controls[1] == 2 and target == 1:
        p[target], p[controls[1]] = p[controls[1]], p[target]
        p1[0], p1[controls[0]] = p1[controls[0]], p1[0]
        p = [p1[p[k]] for k in range(N)]

    elif controls[0] == 1 and controls[1] == 2:
        #  controls[0] -> controls[1] -> target -> outside
        p[0], p[1] = p[1], p[0]
        p[0], p[2] = p[2], p[0]
        p[0], p[target] = p[target], p[0]

    elif controls[0] == 2 and target == 1:
        #  controls[0] -> target -> controls[1] -> outside
        p[0], p[2] = p[2], p[0]
        p[0], p[1] = p[1], p[0]
        p[0], p[controls[1]] = p[controls[1]], p[0]

    elif controls[1] == 0 and controls[0] == 2:
        #  controls[1] -> controls[0] -> target -> outside
        p[1], p[0] = p[0], p[1]
        p[1], p[2] = p[2], p[1]
        p[1], p[target] = p[target], p[1]

    elif controls[1] == 2 and target == 0:
        #  controls[1] -> target -> controls[0] -> outside
        p[1], p[2] = p[2], p[1]
        p[1], p[0] = p[0], p[1]
        p[1], p[controls[0]] = p[controls[0]], p[1]

    elif target == 1 and controls[1] == 0:
        #  target -> controls[1] -> controls[0] -> outside
        p[2], p[1] = p[1], p[2]
        p[2], p[0] = p[0], p[2]
        p[2], p[controls[0]] = p[controls[0]], p[2]

    elif target == 0 and controls[0] == 1:
        #  target -> controls[0] -> controls[1] -> outside
        p[2], p[0] = p[0], p[2]
        p[2], p[1] = p[1], p[2]
        p[2], p[controls[1]] = p[controls[1]], p[2]

    elif controls[0] == 0 and controls[1] == 2:
        #  controls[0] -> self, controls[1] -> target -> outside
        p[1], p[2] = p[2], p[1]
        p[1], p[target] = p[target], p[1]

    elif controls[1] == 1 and controls[0] == 2:
        #  controls[1] -> self, controls[0] -> target -> outside
        p[0], p[2] = p[2], p[0]
        p[0], p[target] = p[target], p[0]

    elif target == 2 and controls[0] == 1:
        #  target -> self, controls[0] -> controls[1] -> outside
        p[0], p[1] = p[1], p[0]
        p[0], p[controls[1]] = p[controls[1]], p[0]

    #
    # N >= 4 cases
    #

    elif controls[0] == 1 and controls[1] > 2 and target > 2:
        #  controls[0] -> controls[1] -> outside, target -> outside
        p[0], p[1] = p[1], p[0]
        p[0], p[controls[1]] = p[controls[1]], p[0]
        p[2], p[target] = p[target], p[2]

    elif controls[0] == 2 and controls[1] > 2 and target > 2:
        #  controls[0] -> target -> outside, controls[1] -> outside
        p[0], p[2] = p[2], p[0]
        p[0], p[target] = p[target], p[0]
        p[1], p[controls[1]] = p[controls[1]], p[1]

    elif controls[1] == 2 and controls[0] > 2 and target > 2:
        #  controls[1] -> target -> outside, controls[0] -> outside
        p[1], p[2] = p[2], p[1]
        p[1], p[target] = p[target], p[1]
        p[0], p[controls[0]] = p[controls[0]], p[0]

    else:
        p[0], p[controls[0]] = p[controls[0]], p[0]
        p1[1], p1[controls[1]] = p1[controls[1]], p1[1]
        p2[2], p2[target] = p2[target], p2[2]
        p = [p[p1[p2[k]]] for k in range(N)]

    return tensor([U] + [identity(2)] * (N - 3)).permute(p)
