import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';

declare var numeric 

@Injectable()
export class NumericProvider {

  constructor() {

  }

  SVD(A) {


    return Observable.create(observer => {

    console.log("A")
    console.log(A)

    console.log("A Transposta")
    let AT = this.Transposta(A)
    console.log(AT)

    console.log("ATA - Multiplicação de Matrizes")
    let ATA = numeric.dot(AT, A)
    console.log(ATA)

    console.log("Algoritimo QR")
    let QR = this.AlgoritimoQR(ATA)
    let autoValores = this.VetorDiagonal(QR[1])
    console.log(autoValores)

    console.log("Singular Values")
    let s = this.SqrtMatrix(QR[1])
    s = this.MatrizDiagonal(s)
    console.log(s)

    console.log("S Inverso")
    let sInv = this.Inverso(s)
    console.log(sInv)

    console.log("Autovetores")
    let V = this.AutoVetores(ATA, autoValores)
    let VT = this.Transposta(V)
    console.log(V)

    console.log("U")
    let u = numeric.dot(A,numeric.dot(V,sInv))
    console.log(u)

    console.log("A reconstruida")
    let newA = numeric.dot(u,numeric.dot(s,VT))
    console.log(newA)

    observer.next(u);
    observer.complete();

    })
  }

  AutoVetores(A, autoValores) {

    let aNumRows = A.length
    let aNumCols = A[0].length

    

    let autoVetores = []
    for(let i=0;i<aNumRows;i++){
      autoVetores.push([])
    }

    for (let n = 0; n < autoValores.length; n++) {
      let newA = []
      for (let i = 0; i < aNumRows; i++) {
        let newRow = []
        for (let j = 0; j < aNumCols; j++) {
          if (i == j) {
            newRow.push(A[i][j] - autoValores[n])
          } else {
            newRow.push(A[i][j])
          }
        }
        newA.push(newRow)
      }
      let b = []
      for(let i=0;i<aNumRows;i++){
        b.push(0)
      }
      
      let autoVetor = this.Gauss(newA,b)
  
      let norm = this.Norma(autoVetor)
      autoVetor = this.DivisaoVetorEscalar(autoVetor,norm)
      for(let i=0;i<autoVetor.length;i++){
        autoVetores[i].push(autoVetor[i])
      }
    }
   
    return autoVetores

  }

  AlgoritimoQR(A) {
    let QR = this.GramsChmidt(A)
    for (let i = 0; i < 10; i++) {
      let B = numeric.dot(QR[1], QR[0])
      QR = this.GramsChmidt(B)
    }
    return QR
  }

  GramsChmidt(A) {

    let aNumRows = A.length
    let aNumCols = A[0].length

    let R = this.Zeros(aNumCols, aNumCols)
    let Q = this.Zeros(aNumRows, aNumCols)

    for (let k = 0; k < aNumCols; k++) {
      let colunaK = this.VetorColuna(A, k)
      for (let j = 0; j < k; j++) {
        colunaK = this.DiferencaDeVetores(colunaK, this.MultiplicacaoVetorEscalar(this.VetorColuna(Q, j), this.ProdutoInterno(this.VetorColuna(Q, j), this.VetorColuna(A, k))))
      }
      Q = this.SetColuna(Q, this.DivisaoVetorEscalar(colunaK, this.Norma(colunaK)), k)

      for (let j = k; j < aNumCols; j++) {
        R[k][j] = this.ProdutoInterno(this.VetorColuna(Q, k), this.VetorColuna(A, j))
      }
    }

    return [Q, R]
  }



  //OPERAÇÕES COM VETORES

  Norma(a) {
    let n = 0
    for (let i = 0; i < a.length; i++) {
      n += a[i] * a[i]
    }
    n = Math.sqrt(n)
    return n
  }

  ProdutoInterno(a, b) {
    if (a.length == b.length) {
      let p = 0
      for (let i = 0; i < a.length; i++) {
        p += a[i] * b[i]
      }
      return p
    } else {
      console.log("Falha no produto interno: Verores com tamanhos diferentes. A.length=" + a.length + " B.length=" + b.length)
      return null
    }
  }

  DiferencaDeVetores(a, b) {
    if (a.length == b.length) {
      let v = []
      for (let i = 0; i < a.length; i++) {
        v.push(a[i] - b[i])
      }
      return v
    } else {
      console.log("Falha na diferença de vetores: Verores com tamanhos diferentes. A.length=" + a.length + " B.length=" + b.length)
      return null
    }
  }

  MultiplicacaoVetorEscalar(a, n) {
    let v = []
    for (let i = 0; i < a.length; i++) {
      v.push(a[i] * n)
    }
    return v
  }

  DivisaoVetorEscalar(a, n) {
    let v = []
    for (let i = 0; i < a.length; i++) {
      v.push(a[i] / n)
    }
    return v
  }

  //OPERAÇÃO COM MATRIZES

  Zeros(row, col) {
    let z = []
    for (let i = 0; i < row; i++) {
      let newRow = []
      for (let j = 0; j < col; j++) {
        newRow.push(0)
      }
      z.push(newRow)
    }
    return z
  }

  /*MultiplicacaoMatricial(A, B) {

    let aNumRows = A.length
    let aNumCols = A[0].length
    let bNumRows = B.length
    let bNumCols = B[0].length

    if (aNumCols == bNumRows) {

      let m = []

      for (let ia = 0; ia < aNumRows; ia++) {
        let newRow = []
        for (let jb = 0; jb < bNumCols; jb++) {
          let value = 0
          for (let ja = 0; ja < aNumCols; ja++) {
            //console.log("par: " + A[x][ja].toString() + "*" + B[ja][jb].toString())
            console.log(ia.toString() + " " + jb.toString() + " " + ja.toString())
            value += A[ia][ja] * B[ja][jb]
          }
          newRow.push(value)
        }
        m.push(newRow)
      }
      return m

    } else {
      console.log("Número de colunas de A é diferente do número de linhas de B: A.shape=(" + aNumRows.toSting() + "," + aNumCols.toString() + ") / B.shape=(" + bNumRows.toString() + "," + bNumCols.toString() + ")")
      return null
    }

  }*/

  Transposta(A) {

    let t = []
    for (let j = 0; j < A[0].length; j++) {
      let newRow = []
      for (let i = 0; i < A.length; i++) {
        newRow.push(A[i][j])
      }
      t.push(newRow)
    }

    return t
  }

  VetorColuna(A, n) {
    let c = []
    let aNumRows = A.length
    for (let i = 0; i < aNumRows; i++) {
      c.push(A[i][n])
    }
    return c
  }

  SetColuna(A, c, n) {

    if (c.length == A.length) {

      for (let i = 0; i < A.length; i++) {
        A[i][n] = c[i]
      }
      return A

    } else {
      console.log("Número de linhas de A é diferente do tamanho do vetor: A.shape[0]=" + A.length.toSting() + " / c.length=" + c.length.toString())
      return null
    }
  }

  SqrtMatrix(A) {

    let aNumRows = A.length
    let aNumCols = A[0].length
    let newA = []

    for (let i = 0; i < aNumRows; i++) {
      let newRow = []
      for (let j = 0; j < aNumCols; j++) {
        newRow.push(Math.sqrt(A[i][j]))
      }
      newA.push(newRow)
    }

    return newA
  }

  Inverso(M) {

    if (M.length !== M[0].length) { return; }

    var i = 0, ii = 0, j = 0, dim = M.length, e = 0, t = 0;
    var I = [], C = [];
    for (i = 0; i < dim; i += 1) {

      I[I.length] = [];
      C[C.length] = [];
      for (j = 0; j < dim; j += 1) {

        if (i == j) { I[i][j] = 1; }
        else { I[i][j] = 0; }

        C[i][j] = M[i][j];
      }
    }

    for (i = 0; i < dim; i += 1) {

      e = C[i][i];

      if (e == 0) {

        for (ii = i + 1; ii < dim; ii += 1) {

          if (C[ii][i] != 0) {

            for (j = 0; j < dim; j++) {
              e = C[i][j];
              C[i][j] = C[ii][j];
              C[ii][j] = e;
              e = I[i][j];
              I[i][j] = I[ii][j];
              I[ii][j] = e;
            }

            break;
          }
        }

        e = C[i][i];

        if (e == 0) { return }
      }

      for (j = 0; j < dim; j++) {
        C[i][j] = C[i][j] / e;
        I[i][j] = I[i][j] / e;
      }

      for (ii = 0; ii < dim; ii++) {
        if (ii == i) { continue; }

        e = C[ii][i];

        for (j = 0; j < dim; j++) {
          C[ii][j] -= e * C[i][j];
          I[ii][j] -= e * I[i][j];
        }
      }
    }
    return I;
  }

  MatrizDiagonal(A) {
    let aNumRows = A.length
    let aNumCols = A[0].length

    for (let i = 0; i < aNumRows; i++) {
      for (let j = 0; j < aNumCols; j++) {
        if (i != j) {
          A[i][j] = 0
        }
      }
    }
    return A
  }

  VetorDiagonal(A) {
    let aNumRows = A.length
    let aNumCols = A[0].length

    let v = []
    for (let i = 0; i < aNumRows; i++) {
      for (let j = 0; j < aNumCols; j++) {
        if (i == j) {
          v.push(A[i][j])
        }
      }
    }
    return v
  }

  Gauss(A, b) {

    var i, k, j;

    let aNumRows = A.length
    let aNumCols = A[0].length

    let fullA = []
    for (let i = 0; i < aNumRows; i++) {
      let newRow = []
      for (let j = 0; j < aNumCols + 1; j++) {
        if (j == aNumCols) {
          newRow.push(b[i])
        } else {
          newRow.push(A[i][j])
        }
      }
      fullA.push(newRow)
    }

    for (i = 0; i < aNumRows; i++) {
      // Search for maximum in this column
      var maxEl = Math.abs(fullA[i][i]), maxRow = i;
      for (k = i + 1; k < aNumRows; k++) {
        if (Math.abs(fullA[k][i]) > maxEl) {
          maxEl = Math.abs(fullA[k][i]);
          maxRow = k;
        }
      }

      // Swap maximum row with current row (column by column)
      for (k = i; k < aNumRows + 1; k++) {
        var tmp = fullA[maxRow][k];
        fullA[maxRow][k] = fullA[i][k];
        fullA[i][k] = tmp;
      }

      // Make all rows below this one 0 in current column
      for (k = i + 1; k < aNumRows; k++) {
        var c = -fullA[k][i] / fullA[i][i];
        for (j = i; j < aNumRows + 1; j++) {
          if (i === j) {
            fullA[k][j] = 0;
          } else {
            fullA[k][j] += c * fullA[i][j];
          }
        }
      }
    }
    
    // Solve equation Ax=b for an upper triangular matrix A
    let x = this.array_fill(0, aNumRows, 0);
    
    let newJ = fullA[0].length - 1

    for (i = aNumRows - 1; i > -1; i--) {
      if(Math.abs(fullA[i][i]) < 0.0001 || (fullA[i][newJ] == 0 && i == aNumRows - 1)){
        x[i] = 1
      }else{
        
        x[i] = fullA[i][newJ] / fullA[i][i];
      }
      for (k = i - 1; k > -1; k--) {
        fullA[k][newJ] -= fullA[k][i] * x[i];
      }
    }
  
    return x;
  }

  array_fill(i, n, v) {
    let a = [];
    for (; i < n; i++) {
      a.push(v);
    }
    return a;
  }

}
