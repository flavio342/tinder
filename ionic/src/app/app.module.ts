import { BrowserModule } from '@angular/platform-browser';
import { ErrorHandler, NgModule } from '@angular/core';
import { IonicApp, IonicErrorHandler, IonicModule } from 'ionic-angular';

import { MyApp } from './app.component';
import { HomePage } from '../pages/home/home';
import { PlotPage } from '../pages/plot/plot';
import { DatasetPage } from '../pages/dataset/dataset';

import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

import { IonicStorageModule } from '@ionic/storage';

import { HTTP } from '@ionic-native/http';
import { BrowserTab } from '@ionic-native/browser-tab';
import { File } from '@ionic-native/file';

import { ApiProvider } from '../providers/api/api';
import { AuthProvider } from '../providers/auth/auth';
import { DatasetProvider } from '../providers/dataset/dataset';
import { NumericProvider } from '../providers/numeric/numeric';

@NgModule({
  declarations: [
    MyApp,
    HomePage,
    PlotPage,
    DatasetPage
  ],
  imports: [
    BrowserModule,
    IonicModule.forRoot(MyApp),
    IonicStorageModule.forRoot()
  ],
  bootstrap: [IonicApp],
  entryComponents: [
    MyApp,
    HomePage,
    PlotPage,
    DatasetPage
  ],
  providers: [
    StatusBar,
    SplashScreen,
    {provide: ErrorHandler, useClass: IonicErrorHandler},
    ApiProvider,
    HTTP,
    BrowserTab,
    AuthProvider,
    File,
    DatasetProvider,
    NumericProvider
  ]
})
export class AppModule {}
