import { Component , NgZone} from '@angular/core';
import { IonicPage, NavController, NavParams,  } from 'ionic-angular';

import { ApiProvider } from '../../providers/api/api'
import { AuthProvider } from '../../providers/auth/auth'
import { DatasetProvider } from '../../providers/dataset/dataset';

import { ToastController } from 'ionic-angular';

@IonicPage()
@Component({
  selector: 'page-dataset',
  templateUrl: 'dataset.html',
})
export class DatasetPage {


  currentImg = ""
  currentUploads = []

  isAddingData = false

  IMG_SIZE = 84
  IMG_I = 3

  constructor(private zone: NgZone, public toastCtrl: ToastController, private auth: AuthProvider, private data: DatasetProvider, private api: ApiProvider, public navCtrl: NavController, public navParams: NavParams) {
  }

  ionViewDidLoad() {

  }


  GetImages() {
    this.isAddingData = true;
    let headers = { 'User-Agent': 'Tinder Android Version 3.2.0', 'Content-Type': 'application/json', 'X-Auth-Token': this.auth.tinder_token }
    this.api.Get('https://api.gotinder.com/user/recs', {}, headers).subscribe((data) => {
      let people = JSON.parse(data.data).results
      for (let i = 0; i < people.length; i++) {
        if (people[i].photos[0].processedFiles[this.IMG_I].height == this.IMG_SIZE) {
          this.currentUploads.push(people[i].photos[0].processedFiles[this.IMG_I].url);
        }
      }
      this.ProcessImages()
    }, (error) => {
      this.isAddingData = false;
      this.currentImg = ""
      let error_message = JSON.parse(error.error).error
      let toast = this.toastCtrl.create({
        message: error_message,
        duration: 3000
      });
      toast.present();
    })
  }

  ProcessImages() {

    if (this.currentUploads.length > 0) {

      this.currentImg = this.currentUploads.pop()

      let canvas = document.createElement('canvas');
      canvas.width = this.IMG_SIZE;
      canvas.height = this.IMG_SIZE;
      let context = canvas.getContext('2d');

      let canvasImg = new Image();
      canvasImg.src = this.currentImg

      canvasImg.onload = () => {
        context.drawImage(canvasImg, 0, 0, canvas.width, canvas.height);
        let pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;

        let newEntry = {
          like: false,
          pixels: pixels
        }

        this.data.dataset.push(newEntry)
        this.data.nOfImages = this.data.dataset.length
      
        this.ProcessImages()
      }
    } else {
      this.data.UpdateData().then(() => {
        this.isAddingData = false
        this.currentImg = ""
      }, (error) => {
        this.isAddingData = false;
        this.currentImg = ""
        let toast = this.toastCtrl.create({
          message: error,
          duration: 3000
        });
        toast.present();
      })
    }
  }

}
