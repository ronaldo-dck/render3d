import numpy as np


def calc_luz(s, point, normal, m_ambiente, m_difuso, m_specular, luz_ambiente, luz_prop, luz_pos, n):
    
    comp_ambiente = [m * la for m, la in zip(m_ambiente, luz_ambiente)]
    comp_difusa = [0,0,0]
    comp_specular = [0,0,0]

    normal = np.array(normal)
    luz_pos = np.array(luz_pos)
    point = np.array(point)
    L = luz_pos - point
    l_unit = L/np.linalg.norm(L)
    
    angle_difuso = np.dot(normal, l_unit)
    if angle_difuso > 0:
        comp_difusa = [m * ld  * angle_difuso for m, ld in zip(m_difuso, luz_prop)]
        r = 2*angle_difuso * normal - l_unit
        angle_specular = np.dot(r,s)
        if angle_specular > 0:
            comp_specular = [m * ls * angle_specular**n for m, ls in zip(m_specular, luz_prop)]
    else:
        return comp_ambiente
    
    luz =  [ca + cd + cs for ca, cd, cs in zip(comp_ambiente, comp_difusa, comp_specular)]

    return luz



def calc_luz_phong(s, l_unit, normal, m_ambiente, m_difuso, m_specular, luz_ambiente, luz_prop, n):
    
    comp_ambiente = [m * la for m, la in zip(m_ambiente, luz_ambiente)]
    comp_difusa = [0,0,0]
    comp_specular = [0,0,0]

    normal = np.array(normal)

    angle_difuso = np.dot(normal, l_unit)
    if angle_difuso > 0:
        comp_difusa = [m * ld  * angle_difuso for m, ld in zip(m_difuso, luz_prop)]
        H = l_unit + np.array(s)
        h = H/np.linalg.norm(H)
        angle_specular = np.dot(h,normal)
        if angle_specular > 0:
            comp_specular = [m * ls * angle_specular**n for m, ls in zip(m_specular, luz_prop)]
    else:
        return comp_ambiente
    
    luz =  [ca + cd + cs for ca, cd, cs in zip(comp_ambiente, comp_difusa, comp_specular)]

    return luz


if __name__ == "__main__":
    calc_luz(
        (0.101,	0.097,	0.990), (20.600, 10.800, 36.950), (0.669,	0.378,	0.639),(0.4,0,0),(0.7,0,0),(0.5,0,0),(120,0,0),(150,0,0),(70,20,35),2.15
    )
