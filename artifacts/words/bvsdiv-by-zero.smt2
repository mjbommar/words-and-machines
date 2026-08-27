(set-logic QF_BV)
; W.thm.sdiv0 : bvsdiv x 0 = (ite (bvslt x 0) #x01 #xff). Expected: unsat.
(declare-const x (_ BitVec 8))
(assert (not (= (bvsdiv x #x00) (ite (bvslt x #x00) #x01 #xff))))
(check-sat)
