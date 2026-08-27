(set-logic QF_BV)
; W.thm.urem0 : for all x : BitVec 8, bvurem x 0 = x. Expected: unsat.
(declare-const x (_ BitVec 8))
(assert (not (= (bvurem x #x00) x)))
(check-sat)
