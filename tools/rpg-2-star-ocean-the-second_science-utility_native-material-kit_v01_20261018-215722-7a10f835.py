"""Reusable authored stone/utility forms. Integer clusters only; no noise, gradients or resampling."""
def recessed_bay(layer, x0, x1, courses, arch=False):
    """A load-bearing frame, recessed field, worn sill and deliberate contact-light groups."""
    layer.rect(x0, 108, x1, 158, 'st_mid')
    # Broad depth faces. Upper-left light hits the outer left jamb and the inner right return;
    # the header underside and inner left return remain in deep shade (3-6px, not a one-pixel box).
    layer.rect(x0, 109, x0 + 4, 151, 'st_half_lit')
    layer.rect(x0 + 5, 113, x0 + 10, 149, 'st_deep')
    layer.rect(x1 - 10, 113, x1 - 5, 149, 'st_half_lit')
    layer.rect(x1 - 4, 111, x1, 151, 'st_dk')
    layer.rect(x0 + 11, 118, x1 - 11, 148, 'st_half_dk')
    layer.poly([(x0 + 11,118),(x1 - 11,118),(x1 - 11,145),(x0 + 39,145),(x0 + 39,130),(x0 + 11,130)], 'st_mid')
    layer.rect(x0 + 11, 144, x1 - 11, 148, 'st_dk')
    # Two irregular structural bed joints, leaving broad quiet stone faces between them.
    layer.hline(x0 + 12, x0 + courses[1][0], 131, 'st_dk')
    layer.hline(x0 + courses[1][0], x1 - 12, 135, 'st_half_dk')
    layer.vline(x0 + courses[0][0], 120, 130, 'st_half_dk')
    layer.vline(x0 + courses[2][0], 136, 143, 'st_dk')
    layer.rect(x0,108,x1,110,'st')
    layer.rect(x0 + 4,111,x1 - 3,113,'st_mid')
    layer.rect(x0 + 8,114,x1 - 8,117,'st_deep')
    layer.poly([(x0 + 8,118),(x1 - 8,118),(x1 - 11,121),(x0 + 11,121)],'st_dk')
    if arch:
        # A shallow blind arch explains the larger central structural bay without adding a doorway.
        mid = (x0 + x1) // 2
        for dx, yy in [(45, 113), (36, 111), (26, 109), (13, 108)]:
            layer.rect(mid - dx, yy, mid + dx, yy + 1, 'st_half_lit')
        layer.rect(mid - 5, 108, mid + 4, 113, 'st')
        layer.vline(mid + 4, 109, 113, 'st_dk')
    layer.rect(x0 + 1, 149, x1 - 1, 151, 'st')
    layer.rect(x0 + 1, 152, x1 - 1, 154, 'st_half_dk')
    layer.rect(x0 + 2, 155, x1, 158, 'st_deep')
    layer.hline(x0 + 9, x0 + 24, 151, 'st_dk')
    layer.rect(x1 - 12, 154, x1 - 7, 156, 'st_dk')


def maintenance_path(layer):
    """One continuous, worn service strip joins three fixed stations; no new physical geometry."""
    layer.rect(112, 211, 548, 235, 'dk_b')
    layer.hline(112, 548, 211, 'dk_sh2')
    layer.rect(112, 212, 548, 215, 'dk_c')
    layer.rect(112, 216, 548, 232, 'dk_a')
    layer.hline(112, 548, 233, 'dk_worn')
    layer.rect(112, 234, 548, 235, 'dk_sh')
    # Broad worn concrete masses run across station boundaries; no equal grid or repeated highlight stamps.
    layer.poly([(129,224),(188,219),(315,219),(351,223),(346,229),(237,231),(147,230)],'dk_worn')
    layer.poly([(363,220),(421,218),(514,222),(535,227),(492,231),(389,229)],'dk_b')
    layer.line(270,216,270,222,'dk_b')
    layer.line(270,222,274,226,'dk_b')
    layer.line(274,226,274,232,'dk_b')
    layer.line(442,216,442,220,'dk_c')
    for x in [113, 547]:
        layer.vline(x, 216, 232, 'dk_sh')


def aged_base(layer, palette, x0, y0, x1, y1):
    """Recolour only existing stone texels; antenna/pedestal alpha and hardware remain exact."""
    stone={tuple(int(v[i:i+2],16) for i in (1,3,5)) for k,v in palette.items() if k.startswith('st') or k in ('mortar','lichen')}
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            if layer.a[y,x,3] != 255 or tuple(layer.a[y,x,:3]) not in stone:
                continue
            tone='st' if y<y0+4 else 'st_half_dk' if x<x0+(x1-x0)*2//3 else 'st_dk'
            if x>=x1-4: tone='st_mid' if y<y0+4 else 'st_deep'
            if y>=y1-2: tone='st_deep'
            if y==y0 and x<x0+(x1-x0)*2//3: tone='st'
            if y==y0+4: tone='st_deep'
            layer.px(x,y,tone)
    for x,y in [(x0+3,y1-4),(x1-5,y0+2)]:
        if layer.a[y,x,3]==255 and tuple(layer.a[y,x,:3]) in stone:
            layer.px(x,y,'st_dk')


def contact_cluster(layer,x0,x1):
    layer.rect(x0,210,x1+1,211,'dk_sh2')
    layer.rect(x0+4,212,x1+4,213,'dk_sh')
    layer.hline(x0+10,x1+6,214,'dk_b')
