import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

import { LoadingController } from 'ionic-angular';

import { DatasetProvider } from '../../providers/dataset/dataset';
import { NumericProvider } from '../../providers/numeric/numeric';

@IonicPage()
@Component({
  selector: 'page-plot',
  templateUrl: 'plot.html',
})
export class PlotPage {

  A = []

  constructor(public numeric: NumericProvider, public loadingCtrl: LoadingController, private data: DatasetProvider, public navCtrl: NavController, public navParams: NavParams) {
  }

  ionViewDidLoad() {

  }

  PlotData() {
    let loader = this.loadingCtrl.create({
      content: "Please wait..."
    });
    loader.present()
    this.A = []
    for (let i = 0; i < this.data.dataset.length; i++) {
      this.A.push(this.data.dataset[i].pixels)
    }
    if (this.A.length > 0) {
      console.log([this.A.length, this.A[0].length])
    }
    console.log(this.A)
    this.numeric.SVD(this.A).subscribe((u) => {
      console.log("done")
      console.log(u.length)
      console.log(u[0].length)
      loader.dismiss()
    })

  }

  PlotExample(){
    let A = [[4,0],[3,-5]]
    this.numeric.SVD(A).subscribe((u) => {
    
    })
  }



}
