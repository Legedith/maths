; benchmark generated from python API
(set-info :status unknown)
(declare-fun v2 () Real)
(declare-fun v1 () Real)
(declare-fun v0 () Real)
(assert
 (= (+ (+ (+ 0.0 (* 3.0 v0)) (* (- 2.0) v1)) (* (- 1.0) v2)) 1.0))
(assert
 (= (+ (+ (+ 0.0 (* (- 2.0) v0)) (* 3.0 v1)) (* (- 1.0) v2)) (- 1.0)))
(assert
 (= (+ (+ (+ 0.0 (* (- 1.0) v0)) (* (- 1.0) v1)) (* 2.0 v2)) 0.0))
(assert
 (= v1 0.0))
(assert
 (> 2.0 0.0))
(assert
 (> 1.0 0.0))
(assert
 (> 1.0 0.0))
(assert
 (> 5.0 0.0))
(assert
 (> 3.0 0.0))
(assert
 (and (distinct 10.0 0.0) true))
(assert
 (and (distinct 6.0 0.0) true))
(assert
 (and (distinct (/ 1.0 3.0) (- v0 v1)) true))
(check-sat)
