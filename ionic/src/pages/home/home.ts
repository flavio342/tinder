import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

import { Storage } from '@ionic/storage';
import { LoadingController } from 'ionic-angular';
import { ToastController } from 'ionic-angular';
import { BrowserTab } from '@ionic-native/browser-tab';

import { ApiProvider } from '../../providers/api/api'
import { AuthProvider } from '../../providers/auth/auth'
import { DatasetProvider } from '../../providers/dataset/dataset';

@IonicPage()
@Component({
  selector: 'page-home',
  templateUrl: 'home.html',
})
export class HomePage {

  constructor(private data: DatasetProvider, private auth: AuthProvider, private browserTab: BrowserTab, private api: ApiProvider, public toastCtrl: ToastController, public loadingCtrl: LoadingController, public storage: Storage, public navCtrl: NavController, public navParams: NavParams) {
  }

  ionViewDidLoad() {
    if (!this.auth.isLoggedIn) {
      this.storage.get('facebook_credentials').then((val) => {
        if (val) {
          this.auth.facebook_credentials = val
          this.LogIn();
        }
      });
    }
  }

  GoToHelpFindCredentials() {
    this.browserTab.isAvailable()
      .then((isAvailable: boolean) => {
        if (isAvailable) {
          this.browserTab.openUrl('https://gist.github.com/taseppa/66fc7239c66ef285ecb28b400b556938');
        }
      });
  }

  LogIn() {
    let loader = this.loadingCtrl.create({
      content: "Please wait..."
    });
    loader.present()
    this.storage.set('facebook_credentials', this.auth.facebook_credentials).then(() => {

      let loginCredentials = { 'facebook_token': this.auth.facebook_credentials.token, 'facebook_id': this.auth.facebook_credentials.id }
      let headers = { 'Content-Type': 'application/json', 'User-Agent': 'Tinder Android Version 3.2.0' }

      this.api.Post("https://api.gotinder.com/auth", loginCredentials, headers).subscribe((data) => {
        this.auth.tinder_token = JSON.parse(data.data).token
        this.auth.user = JSON.parse(data.data).user
        console.log(this.auth.user)
        this.data.GetDataset().then(() => {
          loader.dismiss()
          this.auth.isLoggedIn = true
        }, (error) => {
          loader.dismiss()
          let toast = this.toastCtrl.create({
            message: "Couldn't load dataset",
            duration: 3000
          });
          toast.present();
        })
      }, (error) => {
        loader.dismiss()
        let error_message = ""
        if (error.status == '400') {
          error_message = "Facebook credentials not found..."
        } else if (error.status == '401') {
          error_message = "Tinder token expired..."
        } else {
          error_message = JSON.parse(error.error).error
        }
        let toast = this.toastCtrl.create({
          message: error_message,
          duration: 3000
        });
        toast.present();
      })

    })
  }

}
