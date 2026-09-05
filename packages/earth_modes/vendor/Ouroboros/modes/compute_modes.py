"""Selected Ouroboros v6.0 assembly routines, with attributed local fixes.

The unused upstream file pipeline is deliberately excluded. Public callers use
Earth Modes' SI adapter; see vendor/README.md for scientific modifications.
"""
import numpy as np
from scipy.linalg import eigh, block_diag
import scipy.sparse as sps
from earth_modes.vendor.Ouroboros.modes import FEM, lib
G = 6.6723e-2  # Internal units; matches the pinned MINEOS reference.

def build_matrices_toroidal_and_solve(model, count_thick, i, invV, order, Dr):
    '''
    Construct mass and stiffness matrices for toroidal modes, and solve the
    eigenvalue equation.
    '''

    cur_model = lib.modelDiv(model,np.arange(count_thick[i],count_thick[i+1]))
    # generate matrices A and B such that Ax  =  omega^2*Bx
    [A,B] = FEM.toroidal(cur_model,invV,order,Dr)
    
    if count_thick[i]==0:
        eigvals, reduced = eigh(A[1:,1:],B[1:,1:])
        eigvecs = np.vstack((np.zeros(reduced.shape[1]),reduced))
    else:
        eigvals,eigvecs = eigh(A,B)

    return eigvals, eigvecs


def build_matrices_radial_or_spheroidal(
        l, model, count_thick,
        invV, invV_p, invV_V, invV_P,
        order, order_p, order_V, order_P,
        Dr, Dr_p, Dr_V, Dr_P,
        rho, radius,
        block_type, brk_radius, brk_num, layers, switch):
    '''
    Construct mass and stiffness matrix for radial or spheroidal modes.
    '''
    
    # Calculate k (asymptotic wavenumber).
    k = np.sqrt(l*(l + 1.0))

    # Set model parameters.
    model.set_k(k)
    # generate matrices A and B such that Ax  =  omega^2*Bx
    A = []
    B = []
    #length of U,V,p,P, etc
    #U,V for solid, U,V,p for fluid
    block_len = []
    block_pos = [0]
    
    for i in range(layers):
        cur_model = lib.modelDiv(model,np.arange(count_thick[i],count_thick[i+1]))
        #basically follow the original order
        if block_type[i] == 0:

            if switch == 'S_noGP':

                [tempA,tempB,temp_block_len] = FEM.fluid_noG_mixedV(cur_model,invV,invV_p,invV_V,order,order_p,order_V,Dr,Dr_p,Dr_V)

            elif switch == 'S_G':

                [tempA,tempB,temp_block_len] = FEM.fluid_G_mixedV(cur_model,invV,invV_p,invV_V,order,order_p,order_V,Dr,Dr_p,Dr_V,rho,radius)

            elif switch == 'S_GP':

                [tempA,tempB,temp_block_len] = FEM.fluid_GP_mixedPV(cur_model,invV,invV_p,invV_P,invV_V,order,order_p,order_P,order_V,Dr,Dr_p,Dr_P,Dr_V,rho,radius)

            elif switch == 'R_noGP':

                [tempA,tempB,temp_block_len] = FEM.radial_fluid_noG_mixedV(cur_model,invV,invV_p,order,order_p,Dr,Dr_p)

            elif switch == 'R_G':

                [tempA,tempB,temp_block_len] = FEM.radial_fluid_G_mixedV(cur_model,invV,invV_p,order,order_p,Dr,Dr_p,rho,radius)

            elif switch == 'R_GP':

                [tempA,tempB,temp_block_len] = FEM.radial_fluid_GP_mixedPV(cur_model,invV,invV_p,invV_P,order,order_p,order_P,Dr,Dr_p,Dr_P,rho,radius)

            #block_type.append(0)
            #cut off singularity in pressure after boundary condition
        else:

            if switch == 'S_noGP':

                [tempA,tempB,temp_block_len] = FEM.solid_noG(cur_model,invV,order,Dr)

            elif switch == 'S_G':

                [tempA,tempB,temp_block_len] = FEM.solid_G(cur_model,invV,order,Dr,rho,radius)

            elif switch == 'S_GP':

                [tempA,tempB,temp_block_len] = FEM.solid_GPmixed(cur_model,invV,invV_P,order,order_P,Dr,Dr_P,rho,radius)

            elif switch == 'R_noGP':

                [tempA,tempB,temp_block_len] = FEM.radial_solid_noG(cur_model,invV,order,Dr)

            elif switch == 'R_G':

                [tempA,tempB,temp_block_len] = FEM.radial_solid_G(cur_model,invV,order,Dr,rho,radius)

            elif switch == 'R_GP':

                [tempA,tempB,temp_block_len] = FEM.radial_solid_GPmixed(cur_model,invV,invV_P,order,order_P,Dr,Dr_P,rho,radius)

            #block_type.append(1)
            
        if i == 0:

            A = tempA
            B = tempB

        else:

            A = block_diag(A,tempA)
            B = block_diag(B,tempB)

        block_len.append(temp_block_len)
        for j in range(len(temp_block_len)):
            block_pos.append(block_pos[-1]+temp_block_len[j])

    if switch in ['R_GP', 'S_GP']:
        potential_block = 1 if switch == 'R_GP' else 2
        potential_end = sum(sum(b) for b in block_len[:-1]) + sum(block_len[-1][:potential_block + 1]) - 1
        P_end = brk_radius[-1]*(1 if switch == 'R_GP' else l+1)/(4*np.pi*G)
        A[potential_end,potential_end] += P_end
    
    # impose boundary condition
    C = np.zeros(np.shape(A))
    count_blk_size = 0
    for i in range(layers-1):
        count_blk_size = count_blk_size + np.sum(block_len[i])
        if block_type[i] == 1: #solid-fluid
            # manage unit: *1e12/1e15

            if switch in ['S_noGP', 'S_G', 'R_GP']: 

                C[count_blk_size+block_len[i+1][0]+block_len[i+1][1],count_blk_size-np.sum(block_len[i])+block_len[i][0]-1] = brk_radius[i+1]**2*1e-3
                C[count_blk_size-np.sum(block_len[i])+block_len[i][0]-1,count_blk_size+block_len[i+1][0]+block_len[i+1][1]] = brk_radius[i+1]**2*1e-3

            elif switch == 'S_GP':

                C[count_blk_size+block_len[i+1][0]+block_len[i+1][1]+block_len[i+1][2],count_blk_size-np.sum(block_len[i])+block_len[i][0]-1] = brk_radius[i+1]**2*1e-3
                C[count_blk_size-np.sum(block_len[i])+block_len[i][0]-1,count_blk_size+block_len[i+1][0]+block_len[i+1][1]+block_len[i+1][2]] = brk_radius[i+1]**2*1e-3

            elif switch in ['R_noGP', 'R_G']:
                
                C[count_blk_size+block_len[i+1][0],count_blk_size-np.sum(block_len[i])+block_len[i][0]-1] = brk_radius[i+1]**2*1e-3
                C[count_blk_size-np.sum(block_len[i])+block_len[i][0]-1,count_blk_size+block_len[i+1][0]] = brk_radius[i+1]**2*1e-3

            if switch in ['R_G', 'R_GP', 'S_G', 'S_GP']:

                g_Rc_plus = lib.gravfield(brk_radius[i+1],rho,radius)
                C[count_blk_size-np.sum(block_len[i])+block_len[i][0]-1,count_blk_size-np.sum(block_len[i])+block_len[i][0]-1] = -rho[brk_num[i+1]]*g_Rc_plus*brk_radius[i+1]**2

        else: #fluid-solid

            # manage unit: *1e12/1e15
            C[count_blk_size-1,count_blk_size] = -brk_radius[i+1]**2*1e-3
            C[count_blk_size,count_blk_size-1] = -brk_radius[i+1]**2*1e-3

            if switch in ['R_G', 'R_GP', 'S_G', 'S_GP']:
        
                g_Rb_minus = lib.gravfield(brk_radius[i+1],rho,radius)
                C[count_blk_size,count_blk_size] = rho[brk_num[i+1]-1]*g_Rb_minus*brk_radius[i+1]**2
    # Free fluid exterior: remove the pressure integration boundary term.
    # The Lagrangian normal traction vanishes: p = rho*g*U.
    if block_type[-1] == 0:
        outer_u = sum(sum(b) for b in block_len[:-1]) + block_len[-1][0] - 1
        outer_p = len(A)-1
        C[outer_u,outer_p] -= brk_radius[-1]**2*1e-3
        C[outer_p,outer_u] -= brk_radius[-1]**2*1e-3
        if switch in ['R_G','R_GP','S_G','S_GP']:
            C[outer_u,outer_u] += rho[-1]*lib.gravfield(brk_radius[-1],rho,radius)*brk_radius[-1]**2
    #A_bdr_cond = A+C
    #B_bdr_cond = B
    # sparse matrix version
    # It is hard to use scipy.sparse, so the implimentation is subtle here for sparse matrix
    A_bdr_cond = sps.csc_matrix(A+C)
    B_bdr_cond = sps.csc_matrix(B)
    
    A_singularity, B_singularity, A0_inv, E_singularity, B_eqv_pressure = _reduce_mixed(
        block_type, block_len, A_bdr_cond, B_bdr_cond,
        switch.startswith('S'), switch.endswith('_GP'), l)


    return A_singularity, B_singularity, A0_inv, E_singularity, B_eqv_pressure, block_type, block_len


def _reduce_mixed(block_type, block_len, A, B, spheroidal, potential, degree=0):
    A = A.toarray() if sps.issparse(A) else np.asarray(A)
    B = B.toarray() if sps.issparse(B) else np.asarray(B)
    original = [list(b) for b in block_len]
    offsets = np.r_[0, np.cumsum([sum(b) for b in original])]
    keep = list(range(len(A)))
    displacement_blocks = 2 if spheroidal else 1
    potential_index = displacement_blocks
    remove = []
    if potential:
        # Identify the two interface potential values, retaining the left one.
        for i in range(len(original)-1):
            left = offsets[i]+sum(original[i][:potential_index+1])-1
            right = offsets[i+1]+sum(original[i+1][:potential_index])
            A[left,:] += A[right,:]; A[:,left] += A[:,right]
            B[left,:] += B[right,:]; B[:,left] += B[:,right]
            remove.append(int(right))
    # Mixed pressure has no regular centre DOF (its r=0 test function is null).
    if block_type[0] == 0:
        remove.append(sum(original[0][:-1]))
    keep = np.array([i for i in keep if i not in remove])
    A = A[np.ix_(keep,keep)]; B = B[np.ix_(keep,keep)]
    auxiliary = []
    for i, blocks in enumerate(original):
        start = offsets[i]+sum(blocks[:displacement_blocks])
        auxiliary.extend(range(start,offsets[i+1]))
    aux = np.flatnonzero(np.isin(keep,auxiliary))
    free = np.flatnonzero(~np.isin(keep,auxiliary))
    if len(aux):
        E = A[np.ix_(free,aux)]
        condensed = A[np.ix_(free,free)] - E @ np.linalg.solve(A[np.ix_(aux,aux)],E.T)
    else:
        condensed = A
    mass = B[np.ix_(free,free)]
    condensed = (condensed+condensed.T)/2
    for i in range(len(block_len)):
        block_len[i][:] = original[i][:displacement_blocks]
    centre = [0,block_len[0][0]] if spheroidal else [0]
    retained = np.delete(np.arange(len(condensed)),centre)
    # Exact spherical regularity, including finite rigid-translation l=1
    # centre values. Congruence retains the centre mass, unlike static
    # condensation of a nearly singular elastic centre stiffness block.
    transform = np.eye(len(condensed))[:,retained]
    if spheroidal and degree == 1:
        # The collocated centre has exactly zero mass. Regular even U(r)
        # extrapolation from the first midpoint and endpoint avoids introducing
        # a massless algebraic DOF; its O(h^4) error is convergence checked.
        transform[centre[0],0:2] = [4/3,-1/3]
        transform[centre[1],0:2] = np.sqrt(2)*np.array([4/3,-1/3])
    final = transform.T@condensed@transform
    final_mass = transform.T@mass@transform
    return (final+final.T)/2, (final_mass+final_mass.T)/2, None, transform, mass
