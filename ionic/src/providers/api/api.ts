import { Injectable } from '@angular/core';

import { HTTP } from '@ionic-native/http';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class ApiProvider {

  constructor(public http: HTTP) {

  }

  Get(url, body, headers) {
    return Observable.create(observer => {
      this.http.get(url, body, headers).then(
        data => {
          observer.next(data);
          observer.complete();
        },
        error => {
          observer.error(error);
          observer.complete();
        }
      );
    });
  }

  Post(url, body, headers) {
    return Observable.create(observer => {
      this.http.post(url, body, headers).then(
        data => {
          observer.next(data);
          observer.complete();
        },
        error => {
          observer.error(error);
          observer.complete();
        }
      );
    });
  }

}
