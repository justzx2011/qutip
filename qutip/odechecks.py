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
import numpy as np
from types import FunctionType, BuiltinFunctionType
from functools import partial
from qutip.qobj import *


def _ode_checks(H, c_ops, solver='me'):
    """
    Checks on time-dependent format.
    """
    h_const = []
    h_func = []
    h_str = []
    # check H for incorrect format
    if isinstance(H, Qobj):
        pass
    elif isinstance(H, (FunctionType, BuiltinFunctionType, partial)):
        pass  # n_func += 1
    elif isinstance(H, list):
        for k, H_k in enumerate(H):
            if isinstance(H_k, Qobj):
                h_const.append(k)
            elif isinstance(H_k, list):
                if len(H_k) != 2 or not isinstance(H_k[0], Qobj):
                    raise TypeError("Incorrect hamiltonian specification")
                else:
                    if isinstance(H_k[1], (FunctionType,
                                           BuiltinFunctionType, partial)):
                        h_func.append(k)
                    elif isinstance(H_k[1], str):
                        h_str.append(k)
                    elif isinstance(H_k[1], np.ndarray):
                        h_str.append(k)
                    else:
                        raise TypeError("Incorrect hamiltonian specification")
    else:
        raise TypeError("Incorrect hamiltonian specification")

    # the the whole thing again for c_ops
    c_const = []
    c_func = []
    c_str = []
    if isinstance(c_ops, list):
        for k in range(len(c_ops)):
            if isinstance(c_ops[k], Qobj):
                c_const.append(k)
            elif isinstance(c_ops[k], list):
                if len(c_ops[k]) != 2 or not isinstance(c_ops[k][0], Qobj):
                    raise TypeError(
                        "Incorrect collapse operator specification")
                else:
                    if isinstance(c_ops[k][1], (FunctionType,
                                                BuiltinFunctionType, partial)):
                        c_func.append(k)
                    elif isinstance(c_ops[k][1], str):
                        c_str.append(k)
                    elif isinstance(c_ops[k][1], np.ndarray):
                        c_str.append(k)
                    else:
                        raise TypeError(
                            "Incorrect collapse operator specification")
    else:
        raise TypeError("Incorrect collapse operator specification")

    #
    # if n_str == 0 and n_func == 0:
    #     # no time-dependence at all
    #
    if ((len(h_str) > 0 and len(h_func) > 0) or
            (len(c_str) > 0 and len(c_func) > 0)):
        raise TypeError(
            "Cannot mix string and function type time-dependence formats")

    # check to see if Cython is installed and version is high enough.
    if len(h_str) > 0 or len(c_str) > 0:
        try:
            import Cython
        except:
            raise Exception(
                "Unable to load Cython. Use Python function format.")
        else:
            if Cython.__version__ < '0.14':
                raise Exception("Cython version (%s) is too old. Upgrade to " +
                                "version 0.14+" % Cython.__version__)

    if solver == 'me':
        return (len(h_const + c_const),
                len(h_func) + len(c_func),
                len(h_str) + len(c_str))
    elif solver == 'mc':

        #   H      C_ops    #
        #   --     -----    --
        #   NO      NO      00
        #   NO     STR      01
        #   NO     FUNC     02
        #
        #   STR    NO       10
        #   STR    STR      11
        #
        #   FUNC   NO       20
        #
        #   FUNC   FUNC     22

        if isinstance(H, FunctionType):
            time_type = 3
        # Time-indepdent problems
        elif ((len(h_func) == len(h_str) == 0) and
                (len(c_func) == len(c_str) == 0)):
            time_type = 0

        # constant Hamiltonian, time-dependent collapse operators
        elif len(h_func) == len(h_str) == 0:
            if len(c_str) > 0:
                time_type = 1
            elif len(c_func) > 0:
                time_type = 2
            else:
                raise Exception("Error determining time-dependence.")

        # list style Hamiltonian
        elif len(h_str) > 0:
            if len(c_func) == len(c_str) == 0:
                time_type = 10
            elif len(c_str) > 0:
                time_type = 11
            else:
                raise Exception("Error determining time-dependence.")

        # Python function style Hamiltonian
        elif len(h_func) > 0:
            if len(c_func) == len(c_str) == 0:
                time_type = 20
            elif len(c_func) > 0:
                time_type = 22
            else:
                raise Exception("Error determining time-dependence.")

        return time_type, [h_const, h_func, h_str], [c_const, c_func, c_str]


def _td_wrap_array_str(H, c_ops, args, times):
    """
    Wrap numpy-array based time-dependence in the string-based time dependence
    format
    """
    n = 0
    H_new = []
    c_ops_new = []
    args_new = {}

    if not isinstance(H, list):
        H_new = H
    else:
        for Hk in H:
            if isinstance(Hk, list) and isinstance(Hk[1], np.ndarray):
                H_op, H_td = Hk
                td_array_name = "_td_array_%d" % n
                H_td_str = '(0 if (t > %f) else %s[round(%d * (t/%f))])' %\
                    (times[-1], td_array_name, len(times) - 1, times[-1])
                args_new[td_array_name] = H_td
                H_new.append([H_op, H_td_str])
                n += 1
            else:
                H_new.append(Hk)

    if not isinstance(c_ops, list):
        c_ops_new = c_ops
    else:
        for ck in c_ops:
            if isinstance(ck, list) and isinstance(ck[1], np.ndarray):
                c_op, c_td = ck
                td_array_name = "_td_array_%d" % n
                c_td_str = '(0 if (t > %f) else %s[round(%d * (t/%f))])' %\
                    (times[-1], td_array_name, len(times) - 1, times[-1])
                args_new[td_array_name] = c_td
                c_ops_new.append([c_op, c_td_str])
                n += 1
            else:
                c_ops_new.append(ck)

    if args:
        if isinstance(args, dict):
            args_new.update(args)
        elif not args_new:
            args_new = args
        else:
            raise ValueError("Time-dependent array format requires args to " +
                             "be a dictionary")

    return H_new, c_ops_new, args_new
