export enum ExceptionType {
  InternalLocalError, // internal angular app error
  ExpectationFailed, // http 417
  Unauthorized, // http 401
  BadRequest, // http 400
  Conflict, // http 409
  InternalServerError, // http 500
  NotFound, // http 404
  OtherHttpError, // http other
  LocalSignalrError, // local signal app error
  ServerSignalrError, // server signal app error
  ResultModelIsNull, // the model of BaseResult is null
  RequestFailed, // server returns a action result that indicate the create/update/delete request is failed
  PartialSuccess, // http 512
  SuccessWithWarning // http 513
}
