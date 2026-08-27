(set-logic QF_BV)
; W.thm.udiv0 : for all x : BitVec 8, bvudiv x 0 = #xff  (SMT-LIB totality convention)
; Negated: satisfiable iff the theorem is FALSE. Expected verdict: unsat.
(declare-const x (_ BitVec 8))
(assert (not (= (bvudiv x #x00) #xff)))
(check-sat)
