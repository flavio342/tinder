import { Injectable } from '@angular/core';

import { AuthProvider } from '../../providers/auth/auth'
import { ApiProvider } from '../../providers/api/api'
import { File } from '@ionic-native/file';

@Injectable()
export class DatasetProvider {

  freeDisk = ""
  nOfImages

  dataset = []

  DIR_NAME = "matchMe"
  FILE_NAME = "dataset"

  

  constructor(private api: ApiProvider, private file: File, private auth: AuthProvider) {

  }

  GetDataset() {
    return new Promise((resolve, reject) => {

      this.UpdateData()

      this.file.getFreeDiskSpace().then((val) => {
        this.freeDisk = (val / 1000000).toFixed(2).toString() + " gb";
      })

      this.file.checkDir(this.file.dataDirectory, this.DIR_NAME).then(() => {
        console.log("directory exists")
        this.file.checkFile(this.file.dataDirectory + this.DIR_NAME + "/", this.FILE_NAME).then(() => {
          console.log("file existis")
          this.file.readAsText(this.file.dataDirectory + this.DIR_NAME + "/", this.FILE_NAME).then((data) => {
            console.log("reading from file")
            this.dataset = JSON.parse(data)
            console.log("initial dataset: " + this.dataset.length);
            this.nOfImages = this.dataset.length
            resolve()
          }, (error) => {
            console.log(error)
            reject()
          })
        }, (error) => {
          console.log("file doesnt exists")
          this.file.createFile(this.file.dataDirectory + this.DIR_NAME, this.FILE_NAME, false).then(() => {
            console.log("file created")
            this.file.writeExistingFile(this.file.dataDirectory + this.DIR_NAME + "/", this.FILE_NAME, "[").then(() => {
              console.log("file set")
              this.dataset = []
              this.nOfImages = "0";
              resolve()
            }, (error) => {
              console.log(error)
              reject()
            })
          }, (error) => {
            console.log(error)
            reject()
          })
        })
      }, (error) => {
        console.log("directory not found")
        this.file.createDir(this.file.dataDirectory, this.DIR_NAME, false).then(() => {
          console.log("directory created")
          this.GetDataset().then(() => {
            resolve()
          }, (error) => {
            reject()
          })
        }, (error) => {
          console.log(error)
          reject()
        })
      });
    })
  }

  UpdateData() {
    return new Promise((resolve, reject) => {
      console.log("Before update dataset: " + this.dataset.length)
      this.file.writeExistingFile(this.file.dataDirectory + this.DIR_NAME + "/", this.FILE_NAME, JSON.stringify(this.dataset)).then(() => {
        console.log("data done uploading")
        this.file.getFreeDiskSpace().then((val) => {
          console.log("After update dataset: " + this.dataset.length)
          this.nOfImages = this.dataset.length
          this.freeDisk = (val / 1000000).toFixed(2).toString() + " gb";
        })
        resolve()
      }, (error) => {
        console.log(error)
        reject(error)
      })
    })
  }

}
