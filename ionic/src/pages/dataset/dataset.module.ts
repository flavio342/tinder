import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { DatasetPage } from './dataset';

@NgModule({
  declarations: [
    DatasetPage,
  ],
  imports: [
    IonicPageModule.forChild(DatasetPage),
  ],
})
export class DatasetPageModule {}
