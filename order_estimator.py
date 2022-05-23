from manga109utils import BoundingBox


interception_ratio_threshold = 0.25

def get_pivot_side(zmin, zmax, pivot):
    if pivot <= zmin:
        return 1
    elif zmax <= pivot:
        return 0
    else:
        pivot_z_ratio = (pivot - zmin) / (zmax - zmin)
        interception_ratio = min(pivot_z_ratio, 1 - pivot_z_ratio)

        if interception_ratio > interception_ratio_threshold:
            return -1
        else:
            return 0 if pivot_z_ratio > 0.5 else 1


class BoxSet(set):
    def get_highest_priority_division(self):
        # Horizontal division
        ydivs = sorted([bb.ymin for bb in self] + [bb.ymax for bb in self])
        for pivot in ydivs:
            division = self.get_pivot_division(pivot,
                                               is_horizontal_division=True)
            if len(division) > 1:
                return division

        # Vertical division
        xdivs = sorted([bb.xmin for bb in self] + [bb.xmax for bb in self], reverse=True)
        for pivot in xdivs:
            division = self.get_pivot_division(pivot,
                                               is_horizontal_division=False)
            if len(division) > 1:
                return division

        # Undividable box set
        return [self]

    def get_pivot_division(self, pivot, is_horizontal_division):
        divs = [BoxSet(), BoxSet()]
        for bb in self:
            if is_horizontal_division:
                side = get_pivot_side(bb.ymin, bb.ymax, pivot)
            else:
                side = get_pivot_side(-bb.xmax, -bb.xmin, -pivot)

            if side == -1:
                return [self]
            else:
                divs[side].add(bb)
        if len(divs[0]) == 0 or len(divs[1]) == 0:
            return [self]
        return divs

    def get_multicut_division(self, cuts):
        curset = self
        cur_division = []
        for cut in cuts:
            pivot, is_horizontal_division = cut
            division = curset.get_pivot_division(pivot, is_horizontal_division)
            if len(division) > 1:
                cur_division.append(division[0])
                curset = division[1]
        if len(cur_division) > 0:
            return cur_division + [curset]
        else:
            return [self]

    def yield_ordered_bbs(self):
        if len(self) == 0:
            pass
        elif len(self) > 1:
            yield self.sum(), False
        else:
            yield next(iter(self)), True

    def sum(self):
        if len(self) == 0:
            return BoundingBox()
        else:
            l = list(self)
            return sum(l[1:], l[0])

class BoxNode(object):
    def __init__(self, bbset, initial_cuts=None):
        if initial_cuts:
            division = bbset.get_multicut_division(initial_cuts)
        else:
            division = [bbset]

        if len(division) == 1:
            division = bbset.get_highest_priority_division()

        isLeaf = len(division) <= 1
        self.division = division if isLeaf else [BoxNode(section) for section in division]

    def yield_ordered_bbs(self):
        for section in self.division:
            for bb in section.yield_ordered_bbs():
                yield bb

class BoxOrderEstimator(object):
    def __init__(self, bbs, pagewidth=None, initial_cut_option=None):
        if initial_cut_option == "two-page-four-panel":
            initial_cuts = [(pagewidth * n / 4, False)
                            for n in reversed(range(1, 4))]
        elif initial_cut_option == "two-page":
            initial_cuts = [(pagewidth / 2, False)]
        else:
            initial_cuts = None

        self.boxnode = BoxNode(BoxSet(bbs), initial_cuts)
        t = tuple(zip(*self.boxnode.yield_ordered_bbs()))
        if len(t) > 0:
            self.ordered_bbs, self.bb_estimation_statuses = t
        else:
            self.ordered_bbs, self.bb_estimation_statuses = (), ()
