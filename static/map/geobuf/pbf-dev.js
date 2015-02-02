!function(e){if("object"==typeof exports&&"undefined"!=typeof module)module.exports=e();else if("function"==typeof define&&define.amd)define([],e);else{var f;"undefined"!=typeof window?f=window:"undefined"!=typeof global?f=global:"undefined"!=typeof self&&(f=self),f.Pbf=e()}}(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

// lightweight Buffer shim for pbf browser build
// based on code from github.com/feross/buffer (MIT-licensed)

module.exports = Buffer;

var ieee754 = require('ieee754');

function Buffer(length) {
    var arr;
    if (length && length.length) {
        arr = length;
        length = arr.length;
    }
    var buf = new Uint8Array(length || 0);
    if (arr) buf.set(arr);

    buf.readUInt32LE = BufferMethods.readUInt32LE;
    buf.writeUInt32LE = BufferMethods.writeUInt32LE;
    buf.readInt32LE = BufferMethods.readInt32LE;
    buf.writeInt32LE = BufferMethods.writeInt32LE;
    buf.readFloatLE = BufferMethods.readFloatLE;
    buf.writeFloatLE = BufferMethods.writeFloatLE;
    buf.readDoubleLE = BufferMethods.readDoubleLE;
    buf.writeDoubleLE = BufferMethods.writeDoubleLE;
    buf.toString = BufferMethods.toString;
    buf.write = BufferMethods.write;
    buf.slice = BufferMethods.slice;
    buf.copy = BufferMethods.copy;

    buf._isBuffer = true;
    return buf;
}

var lastStr, lastStrEncoded;

var BufferMethods = {
    readUInt32LE: function(pos) {
        return ((this[pos]) |
            (this[pos + 1] << 8) |
            (this[pos + 2] << 16)) +
            (this[pos + 3] * 0x1000000);
    },

    writeUInt32LE: function(val, pos) {
        this[pos] = val;
        this[pos + 1] = (val >>> 8);
        this[pos + 2] = (val >>> 16);
        this[pos + 3] = (val >>> 24);
    },

    readInt32LE: function(pos) {
        return ((this[pos]) |
            (this[pos + 1] << 8) |
            (this[pos + 2] << 16)) +
            (this[pos + 3] << 24);
    },

    readFloatLE:  function(pos) { return ieee754.read(this, pos, true, 23, 4); },
    readDoubleLE: function(pos) { return ieee754.read(this, pos, true, 52, 8); },

    writeFloatLE:  function(val, pos) { return ieee754.write(this, val, pos, true, 23, 4); },
    writeDoubleLE: function(val, pos) { return ieee754.write(this, val, pos, true, 52, 8); },

    toString: function(encoding, start, end) {
        var str = '',
            tmp = '';

        start = start || 0;
        end = Math.min(this.length, end || this.length);

        for (var i = start; i < end; i++) {
            var ch = this[i];
            if (ch <= 0x7F) {
                str += decodeURIComponent(tmp) + String.fromCharCode(ch);
                tmp = '';
            } else {
                tmp += '%' + ch.toString(16);
            }
        }

        str += decodeURIComponent(tmp);

        return str;
    },

    write: function(str, pos) {
        var bytes = str === lastStr ? lastStrEncoded : encodeString(str);
        for (var i = 0; i < bytes.length; i++) {
            this[pos + i] = bytes[i];
        }
    },

    slice: function(start, end) {
        return this.subarray(start, end);
    },

    copy: function(buf, pos) {
        pos = pos || 0;
        for (var i = 0; i < this.length; i++) {
            buf[pos + i] = this[i];
        }
    }
};

BufferMethods.writeInt32LE = BufferMethods.writeUInt32LE;

Buffer.byteLength = function(str) {
    lastStr = str;
    lastStrEncoded = encodeString(str);
    return lastStrEncoded.length;
};

Buffer.isBuffer = function(buf) {
    return !!(buf && buf._isBuffer);
};

function encodeString(str) {
    var length = str.length,
        bytes = [];

    for (var i = 0, c, lead; i < length; i++) {
        c = str.charCodeAt(i); // code point

        if (c > 0xD7FF && c < 0xE000) {

            if (lead) {
                if (c < 0xDC00) {
                    bytes.push(0xEF, 0xBF, 0xBD);
                    lead = c;
                    continue;

                } else {
                    c = lead - 0xD800 << 10 | c - 0xDC00 | 0x10000;
                    lead = null;
                }

            } else {
                if (c > 0xDBFF || (i + 1 === length)) bytes.push(0xEF, 0xBF, 0xBD);
                else lead = c;

                continue;
            }

        } else if (lead) {
            bytes.push(0xEF, 0xBF, 0xBD);
            lead = null;
        }

        if (c < 0x80) bytes.push(c);
        else {
            if (c < 0x800) bytes.push(c >> 0x6 | 0xC0, c & 0x3F | 0x80);
            else if (c < 0x10000) bytes.push(c >> 0xC | 0xE0, c >> 0x6 & 0x3F | 0x80, c & 0x3F | 0x80);
            else bytes.push(c >> 0x12 | 0xF0, c >> 0xC & 0x3F | 0x80, c >> 0x6 & 0x3F | 0x80, c & 0x3F | 0x80);
        }
    }
    return bytes;
}

},{"ieee754":3}],2:[function(require,module,exports){
(function (global){
'use strict';

module.exports = Pbf;

var Buffer = global.Buffer || require('./buffer');

function Pbf(buf) {
    this.buf = !Buffer.isBuffer(buf) ? new Buffer(buf || 0) : buf;
    this.pos = 0;
    this.length = this.buf.length;
}

Pbf.Varint  = 0; // varint: int32, int64, uint32, uint64, sint32, sint64, bool, enum
Pbf.Fixed64 = 1; // 64-bit: double, fixed64, sfixed64
Pbf.Bytes   = 2; // length-delimited: string, bytes, embedded messages, packed repeated fields
Pbf.Fixed32 = 5; // 32-bit: float, fixed32, sfixed32

var SHIFT_LEFT_32 = (1 << 16) * (1 << 16),
    SHIFT_RIGHT_32 = 1 / SHIFT_LEFT_32;

Pbf.prototype = {

    destroy: function() {
        this.buf = null;
    },

    // === READING =================================================================

    readFields: function(readField, result, end) {
        end = end || this.length;

        while (this.pos < end) {
            var val = this.readVarint(),
                tag = val >> 3,
                startPos = this.pos;

            readField(tag, result, this);

            if (this.pos === startPos) this.skip(val);
        }
        return result;
    },

    readMessage: function(readField, result) {
        return this.readFields(readField, result, this.readVarint() + this.pos);
    },

    readFixed32: function() {
        var val = this.buf.readUInt32LE(this.pos);
        this.pos += 4;
        return val;
    },

    readSFixed32: function() {
        var val = this.buf.readInt32LE(this.pos);
        this.pos += 4;
        return val;
    },

    // 64-bit int handling is based on github.com/dpw/node-buffer-more-ints (MIT-licensed)

    readFixed64: function() {
        var val = this.buf.readUInt32LE(this.pos) + this.buf.readUInt32LE(this.pos + 4) * SHIFT_LEFT_32;
        this.pos += 8;
        return val;
    },

    readSFixed64: function() {
        var val = this.buf.readUInt32LE(this.pos) + this.buf.readInt32LE(this.pos + 4) * SHIFT_LEFT_32;
        this.pos += 8;
        return val;
    },

    readFloat: function() {
        var val = this.buf.readFloatLE(this.pos);
        this.pos += 4;
        return val;
    },

    readDouble: function() {
        var val = this.buf.readDoubleLE(this.pos);
        this.pos += 8;
        return val;
    },

    readVarint: function() {
        var buf = this.buf,
            val, b, b0, b1, b2, b3;

        b0 = buf[this.pos++]; if (b0 < 0x80) return b0;                 b0 = b0 & 0x7f;
        b1 = buf[this.pos++]; if (b1 < 0x80) return b0 | b1 << 7;       b1 = (b1 & 0x7f) << 7;
        b2 = buf[this.pos++]; if (b2 < 0x80) return b0 | b1 | b2 << 14; b2 = (b2 & 0x7f) << 14;
        b3 = buf[this.pos++]; if (b3 < 0x80) return b0 | b1 | b2 | b3 << 21;

        val = b0 | b1 | b2 | (b3 & 0x7f) << 21;

        b = buf[this.pos++]; val += (b & 0x7f) * 0x10000000;         if (b < 0x80) return val;
        b = buf[this.pos++]; val += (b & 0x7f) * 0x800000000;        if (b < 0x80) return val;
        b = buf[this.pos++]; val += (b & 0x7f) * 0x40000000000;      if (b < 0x80) return val;
        b = buf[this.pos++]; val += (b & 0x7f) * 0x2000000000000;    if (b < 0x80) return val;
        b = buf[this.pos++]; val += (b & 0x7f) * 0x100000000000000;  if (b < 0x80) return val;
        b = buf[this.pos++]; val += (b & 0x7f) * 0x8000000000000000; if (b < 0x80) return val;

        throw new Error('Expected varint not more than 10 bytes');
    },

    readSVarint: function() {
        var num = this.readVarint();
        return num % 2 === 1 ? (num + 1) / -2 : num / 2; // zigzag encoding
    },

    readBoolean: function() {
        return Boolean(this.readVarint());
    },

    readString: function() {
        var end = this.readVarint() + this.pos,
            str = this.buf.toString('utf8', this.pos, end);
        this.pos = end;
        return str;
    },

    readBytes: function() {
        var end = this.readVarint() + this.pos,
            buffer = this.buf.slice(this.pos, end);
        this.pos = end;
        return buffer;
    },

    // verbose for performance reasons; doesn't affect gzipped size

    readPackedVarint: function() {
        var end = this.readVarint() + this.pos, arr = [];
        while (this.pos < end) arr.push(this.readVarint());
        return arr;
    },
    readPackedSVarint: function() {
        var end = this.readVarint() + this.pos, arr = [];
        while (this.pos < end) arr.push(this.readSVarint());
        return arr;
    },
    readPackedBoolean: function() {
        var end = this.readVarint() + this.pos, arr = [];
        while (this.pos < end) arr.push(this.readBoolean());
        return arr;
    },
    readPackedFloat: function() {
        var end = this.readVarint() + this.pos, arr = [];
        while (this.pos < end) arr.push(this.readFloat());
        return arr;
    },
    readPackedDouble: function() {
        var end = this.readVarint() + this.pos, arr = [];
        while (this.pos < end) arr.push(this.readDouble());
        return arr;
    },
    readPackedFixed32: function() {
        var end = this.readVarint() + this.pos, arr = [];
        while (this.pos < end) arr.push(this.readFixed32());
        return arr;
    },
    readPackedSFixed32: function() {
        var end = this.readVarint() + this.pos, arr = [];
        while (this.pos < end) arr.push(this.readSFixed32());
        return arr;
    },
    readPackedFixed64: function() {
        var end = this.readVarint() + this.pos, arr = [];
        while (this.pos < end) arr.push(this.readFixed64());
        return arr;
    },
    readPackedSFixed64: function() {
        var end = this.readVarint() + this.pos, arr = [];
        while (this.pos < end) arr.push(this.readSFixed64());
        return arr;
    },

    skip: function(val) {
        var type = val & 0x7;
        if (type === Pbf.Varint) while (this.buf[this.pos++] > 0x7f);
        else if (type === Pbf.Bytes) this.pos = this.readVarint() + this.pos;
        else if (type === Pbf.Fixed32) this.pos += 4;
        else if (type === Pbf.Fixed64) this.pos += 8;
        else throw new Error('Unimplemented type: ' + type);
    },

    // === WRITING =================================================================

    writeTag: function(tag, type) {
        this.writeVarint((tag << 3) | type);
    },

    realloc: function(min) {
        var length = this.length || 16;

        while (length < this.pos + min) length *= 2;

        if (length != this.length) {
            var buf = new Buffer(length);
            this.buf.copy(buf);
            this.buf = buf;
            this.length = length;
        }
    },

    finish: function() {
        this.length = this.pos;
        this.pos = 0;
        return this.buf.slice(0, this.length);
    },

    writeFixed32: function(val) {
        this.realloc(4);
        this.buf.writeUInt32LE(val, this.pos);
        this.pos += 4;
    },

    writeSFixed32: function(val) {
        this.realloc(4);
        this.buf.writeInt32LE(val, this.pos);
        this.pos += 4;
    },

    writeFixed64: function(val) {
        this.realloc(8);
        this.buf.writeInt32LE(val & -1, this.pos);
        this.buf.writeUInt32LE(Math.floor(val * SHIFT_RIGHT_32), this.pos + 4);
        this.pos += 8;
    },

    writeSFixed64: function(val) {
        this.realloc(8);
        this.buf.writeInt32LE(val & -1, this.pos);
        this.buf.writeInt32LE(Math.floor(val * SHIFT_RIGHT_32), this.pos + 4);
        this.pos += 8;
    },

    writeVarint: function(val) {
        val = +val;

        if (val <= 0x7f) {
            this.realloc(1);
            this.buf[this.pos++] = val;

        } else if (val <= 0x3fff) {
            this.realloc(2);
            this.buf[this.pos++] = ((val >>> 0) & 0x7f) | 0x80;
            this.buf[this.pos++] =  (val >>> 7) & 0x7f;

        } else if (val <= 0x1fffff) {
            this.realloc(3);
            this.buf[this.pos++] = ((val >>>  0) & 0x7f) | 0x80;
            this.buf[this.pos++] = ((val >>>  7) & 0x7f) | 0x80;
            this.buf[this.pos++] =  (val >>> 14) & 0x7f;

        } else if (val <= 0xfffffff) {
            this.realloc(4);
            this.buf[this.pos++] = ((val >>>  0) & 0x7f) | 0x80;
            this.buf[this.pos++] = ((val >>>  7) & 0x7f) | 0x80;
            this.buf[this.pos++] = ((val >>> 14) & 0x7f) | 0x80;
            this.buf[this.pos++] =  (val >>> 21) & 0x7f;

        } else {
            var pos = this.pos;
            while (val >= 0x80) {
                this.realloc(1);
                this.buf[this.pos++] = (val & 0xff) | 0x80;
                val /= 0x80;
            }
            this.realloc(1);
            this.buf[this.pos++] = val | 0;
            if (this.pos - pos > 10) throw new Error("Given varint doesn't fit into 10 bytes");
        }
    },

    writeSVarint: function(val) {
        this.writeVarint(val < 0 ? -val * 2 - 1 : val * 2);
    },

    writeBoolean: function(val) {
        this.writeVarint(Boolean(val));
    },

    writeString: function(str) {
        str = String(str);
        var bytes = Buffer.byteLength(str);
        this.writeVarint(bytes);
        this.realloc(bytes);
        this.buf.write(str, this.pos);
        this.pos += bytes;
    },

    writeFloat: function(val) {
        this.realloc(4);
        this.buf.writeFloatLE(val, this.pos);
        this.pos += 4;
    },

    writeDouble: function(val) {
        this.realloc(8);
        this.buf.writeDoubleLE(val, this.pos);
        this.pos += 8;
    },

    writeBytes: function(buffer) {
        var len = buffer.length;
        this.writeVarint(len);
        this.realloc(len);
        for (var i = 0; i < len; i++) this.buf[this.pos++] = buffer[i];
    },

    writeMessage: function(tag, fn, obj) {
        this.writeTag(tag, Pbf.Bytes);

        this.pos++; // reserve 1 byte for short message length

        // write the message directly to the buffer and see how much was written
        var startPos = this.pos;
        fn(obj, this);
        var len = this.pos - startPos;

        var varintLen =
            len <= 0x7f ? 1 :
            len <= 0x3fff ? 2 :
            len <= 0x1fffff ? 3 :
            len <= 0xfffffff ? 4 : Math.ceil(Math.log(len) / (Math.LN2 * 7));

        // if 1 byte isn't enough for encoding message length, shift the data to the right
        if (varintLen > 1) {
            this.realloc(varintLen - 1);
            for (var i = this.pos - 1; i >= startPos; i--) this.buf[i + varintLen - 1] = this.buf[i];
        }

        // finally, write the message length in the reserved place and restore the position
        this.pos = startPos - 1;
        this.writeVarint(len);
        this.pos += len;
    },

    writePackedVarint:   function(tag, arr) { this.writeMessage(tag, writePackedVarint, arr);   },
    writePackedSVarint:  function(tag, arr) { this.writeMessage(tag, writePackedSVarint, arr);  },
    writePackedBoolean:  function(tag, arr) { this.writeMessage(tag, writePackedBoolean, arr);  },
    writePackedFloat:    function(tag, arr) { this.writeMessage(tag, writePackedFloat, arr);    },
    writePackedDouble:   function(tag, arr) { this.writeMessage(tag, writePackedDouble, arr);   },
    writePackedFixed32:  function(tag, arr) { this.writeMessage(tag, writePackedFixed32, arr);  },
    writePackedSFixed32: function(tag, arr) { this.writeMessage(tag, writePackedSFixed32, arr); },
    writePackedFixed64:  function(tag, arr) { this.writeMessage(tag, writePackedFixed64, arr);  },
    writePackedSFixed64: function(tag, arr) { this.writeMessage(tag, writePackedSFixed64, arr); },

    writeBytesField: function(tag, buffer) {
        this.writeTag(tag, Pbf.Bytes);
        this.writeBytes(buffer);
    },
    writeFixed32Field: function(tag, val) {
        this.writeTag(tag, Pbf.Fixed32);
        this.writeFixed32(val);
    },
    writeSFixed32Field: function(tag, val) {
        this.writeTag(tag, Pbf.Fixed32);
        this.writeSFixed32(val);
    },
    writeFixed64Field: function(tag, val) {
        this.writeTag(tag, Pbf.Fixed64);
        this.writeFixed64(val);
    },
    writeSFixed64Field: function(tag, val) {
        this.writeTag(tag, Pbf.Fixed64);
        this.writeSFixed64(val);
    },
    writeVarintField: function(tag, val) {
        this.writeTag(tag, Pbf.Varint);
        this.writeVarint(val);
    },
    writeSVarintField: function(tag, val) {
        this.writeTag(tag, Pbf.Varint);
        this.writeSVarint(val);
    },
    writeStringField: function(tag, str) {
        this.writeTag(tag, Pbf.Bytes);
        this.writeString(str);
    },
    writeFloatField: function(tag, val) {
        this.writeTag(tag, Pbf.Fixed32);
        this.writeFloat(val);
    },
    writeDoubleField: function(tag, val) {
        this.writeTag(tag, Pbf.Fixed64);
        this.writeDouble(val);
    },
    writeBooleanField: function(tag, val) {
        this.writeVarintField(tag, Boolean(val));
    }
};

function writePackedVarint(arr, pbf)   { for (var i = 0; i < arr.length; i++) pbf.writeVarint(arr[i]);   }
function writePackedSVarint(arr, pbf)  { for (var i = 0; i < arr.length; i++) pbf.writeSVarint(arr[i]);  }
function writePackedFloat(arr, pbf)    { for (var i = 0; i < arr.length; i++) pbf.writeFloat(arr[i]);    }
function writePackedDouble(arr, pbf)   { for (var i = 0; i < arr.length; i++) pbf.writeDouble(arr[i]);   }
function writePackedBoolean(arr, pbf)  { for (var i = 0; i < arr.length; i++) pbf.writeBoolean(arr[i]);  }
function writePackedFixed32(arr, pbf)  { for (var i = 0; i < arr.length; i++) pbf.writeFixed32(arr[i]);  }
function writePackedSFixed32(arr, pbf) { for (var i = 0; i < arr.length; i++) pbf.writeSFixed32(arr[i]); }
function writePackedFixed64(arr, pbf)  { for (var i = 0; i < arr.length; i++) pbf.writeFixed64(arr[i]);  }
function writePackedSFixed64(arr, pbf) { for (var i = 0; i < arr.length; i++) pbf.writeSFixed64(arr[i]); }

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"./buffer":1}],3:[function(require,module,exports){
exports.read = function(buffer, offset, isLE, mLen, nBytes) {
  var e, m,
      eLen = nBytes * 8 - mLen - 1,
      eMax = (1 << eLen) - 1,
      eBias = eMax >> 1,
      nBits = -7,
      i = isLE ? (nBytes - 1) : 0,
      d = isLE ? -1 : 1,
      s = buffer[offset + i];

  i += d;

  e = s & ((1 << (-nBits)) - 1);
  s >>= (-nBits);
  nBits += eLen;
  for (; nBits > 0; e = e * 256 + buffer[offset + i], i += d, nBits -= 8);

  m = e & ((1 << (-nBits)) - 1);
  e >>= (-nBits);
  nBits += mLen;
  for (; nBits > 0; m = m * 256 + buffer[offset + i], i += d, nBits -= 8);

  if (e === 0) {
    e = 1 - eBias;
  } else if (e === eMax) {
    return m ? NaN : ((s ? -1 : 1) * Infinity);
  } else {
    m = m + Math.pow(2, mLen);
    e = e - eBias;
  }
  return (s ? -1 : 1) * m * Math.pow(2, e - mLen);
};

exports.write = function(buffer, value, offset, isLE, mLen, nBytes) {
  var e, m, c,
      eLen = nBytes * 8 - mLen - 1,
      eMax = (1 << eLen) - 1,
      eBias = eMax >> 1,
      rt = (mLen === 23 ? Math.pow(2, -24) - Math.pow(2, -77) : 0),
      i = isLE ? 0 : (nBytes - 1),
      d = isLE ? 1 : -1,
      s = value < 0 || (value === 0 && 1 / value < 0) ? 1 : 0;

  value = Math.abs(value);

  if (isNaN(value) || value === Infinity) {
    m = isNaN(value) ? 1 : 0;
    e = eMax;
  } else {
    e = Math.floor(Math.log(value) / Math.LN2);
    if (value * (c = Math.pow(2, -e)) < 1) {
      e--;
      c *= 2;
    }
    if (e + eBias >= 1) {
      value += rt / c;
    } else {
      value += rt * Math.pow(2, 1 - eBias);
    }
    if (value * c >= 2) {
      e++;
      c /= 2;
    }

    if (e + eBias >= eMax) {
      m = 0;
      e = eMax;
    } else if (e + eBias >= 1) {
      m = (value * c - 1) * Math.pow(2, mLen);
      e = e + eBias;
    } else {
      m = value * Math.pow(2, eBias - 1) * Math.pow(2, mLen);
      e = 0;
    }
  }

  for (; mLen >= 8; buffer[offset + i] = m & 0xff, i += d, m /= 256, mLen -= 8);

  e = (e << mLen) | m;
  eLen += mLen;
  for (; eLen > 0; buffer[offset + i] = e & 0xff, i += d, e /= 256, eLen -= 8);

  buffer[offset + i - d] |= s * 128;
};

},{}]},{},[2])(2)
});
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJidWZmZXIuanMiLCJpbmRleC5qcyIsIm5vZGVfbW9kdWxlcy9pZWVlNzU0L2luZGV4LmpzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBO0FDQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7OztBQy9KQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7O0FDblpBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzQ29udGVudCI6WyIoZnVuY3Rpb24gZSh0LG4scil7ZnVuY3Rpb24gcyhvLHUpe2lmKCFuW29dKXtpZighdFtvXSl7dmFyIGE9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtpZighdSYmYSlyZXR1cm4gYShvLCEwKTtpZihpKXJldHVybiBpKG8sITApO3ZhciBmPW5ldyBFcnJvcihcIkNhbm5vdCBmaW5kIG1vZHVsZSAnXCIrbytcIidcIik7dGhyb3cgZi5jb2RlPVwiTU9EVUxFX05PVF9GT1VORFwiLGZ9dmFyIGw9bltvXT17ZXhwb3J0czp7fX07dFtvXVswXS5jYWxsKGwuZXhwb3J0cyxmdW5jdGlvbihlKXt2YXIgbj10W29dWzFdW2VdO3JldHVybiBzKG4/bjplKX0sbCxsLmV4cG9ydHMsZSx0LG4scil9cmV0dXJuIG5bb10uZXhwb3J0c312YXIgaT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2Zvcih2YXIgbz0wO288ci5sZW5ndGg7bysrKXMocltvXSk7cmV0dXJuIHN9KSIsIid1c2Ugc3RyaWN0JztcblxuLy8gbGlnaHR3ZWlnaHQgQnVmZmVyIHNoaW0gZm9yIHBiZiBicm93c2VyIGJ1aWxkXG4vLyBiYXNlZCBvbiBjb2RlIGZyb20gZ2l0aHViLmNvbS9mZXJvc3MvYnVmZmVyIChNSVQtbGljZW5zZWQpXG5cbm1vZHVsZS5leHBvcnRzID0gQnVmZmVyO1xuXG52YXIgaWVlZTc1NCA9IHJlcXVpcmUoJ2llZWU3NTQnKTtcblxuZnVuY3Rpb24gQnVmZmVyKGxlbmd0aCkge1xuICAgIHZhciBhcnI7XG4gICAgaWYgKGxlbmd0aCAmJiBsZW5ndGgubGVuZ3RoKSB7XG4gICAgICAgIGFyciA9IGxlbmd0aDtcbiAgICAgICAgbGVuZ3RoID0gYXJyLmxlbmd0aDtcbiAgICB9XG4gICAgdmFyIGJ1ZiA9IG5ldyBVaW50OEFycmF5KGxlbmd0aCB8fCAwKTtcbiAgICBpZiAoYXJyKSBidWYuc2V0KGFycik7XG5cbiAgICBidWYucmVhZFVJbnQzMkxFID0gQnVmZmVyTWV0aG9kcy5yZWFkVUludDMyTEU7XG4gICAgYnVmLndyaXRlVUludDMyTEUgPSBCdWZmZXJNZXRob2RzLndyaXRlVUludDMyTEU7XG4gICAgYnVmLnJlYWRJbnQzMkxFID0gQnVmZmVyTWV0aG9kcy5yZWFkSW50MzJMRTtcbiAgICBidWYud3JpdGVJbnQzMkxFID0gQnVmZmVyTWV0aG9kcy53cml0ZUludDMyTEU7XG4gICAgYnVmLnJlYWRGbG9hdExFID0gQnVmZmVyTWV0aG9kcy5yZWFkRmxvYXRMRTtcbiAgICBidWYud3JpdGVGbG9hdExFID0gQnVmZmVyTWV0aG9kcy53cml0ZUZsb2F0TEU7XG4gICAgYnVmLnJlYWREb3VibGVMRSA9IEJ1ZmZlck1ldGhvZHMucmVhZERvdWJsZUxFO1xuICAgIGJ1Zi53cml0ZURvdWJsZUxFID0gQnVmZmVyTWV0aG9kcy53cml0ZURvdWJsZUxFO1xuICAgIGJ1Zi50b1N0cmluZyA9IEJ1ZmZlck1ldGhvZHMudG9TdHJpbmc7XG4gICAgYnVmLndyaXRlID0gQnVmZmVyTWV0aG9kcy53cml0ZTtcbiAgICBidWYuc2xpY2UgPSBCdWZmZXJNZXRob2RzLnNsaWNlO1xuICAgIGJ1Zi5jb3B5ID0gQnVmZmVyTWV0aG9kcy5jb3B5O1xuXG4gICAgYnVmLl9pc0J1ZmZlciA9IHRydWU7XG4gICAgcmV0dXJuIGJ1Zjtcbn1cblxudmFyIGxhc3RTdHIsIGxhc3RTdHJFbmNvZGVkO1xuXG52YXIgQnVmZmVyTWV0aG9kcyA9IHtcbiAgICByZWFkVUludDMyTEU6IGZ1bmN0aW9uKHBvcykge1xuICAgICAgICByZXR1cm4gKCh0aGlzW3Bvc10pIHxcbiAgICAgICAgICAgICh0aGlzW3BvcyArIDFdIDw8IDgpIHxcbiAgICAgICAgICAgICh0aGlzW3BvcyArIDJdIDw8IDE2KSkgK1xuICAgICAgICAgICAgKHRoaXNbcG9zICsgM10gKiAweDEwMDAwMDApO1xuICAgIH0sXG5cbiAgICB3cml0ZVVJbnQzMkxFOiBmdW5jdGlvbih2YWwsIHBvcykge1xuICAgICAgICB0aGlzW3Bvc10gPSB2YWw7XG4gICAgICAgIHRoaXNbcG9zICsgMV0gPSAodmFsID4+PiA4KTtcbiAgICAgICAgdGhpc1twb3MgKyAyXSA9ICh2YWwgPj4+IDE2KTtcbiAgICAgICAgdGhpc1twb3MgKyAzXSA9ICh2YWwgPj4+IDI0KTtcbiAgICB9LFxuXG4gICAgcmVhZEludDMyTEU6IGZ1bmN0aW9uKHBvcykge1xuICAgICAgICByZXR1cm4gKCh0aGlzW3Bvc10pIHxcbiAgICAgICAgICAgICh0aGlzW3BvcyArIDFdIDw8IDgpIHxcbiAgICAgICAgICAgICh0aGlzW3BvcyArIDJdIDw8IDE2KSkgK1xuICAgICAgICAgICAgKHRoaXNbcG9zICsgM10gPDwgMjQpO1xuICAgIH0sXG5cbiAgICByZWFkRmxvYXRMRTogIGZ1bmN0aW9uKHBvcykgeyByZXR1cm4gaWVlZTc1NC5yZWFkKHRoaXMsIHBvcywgdHJ1ZSwgMjMsIDQpOyB9LFxuICAgIHJlYWREb3VibGVMRTogZnVuY3Rpb24ocG9zKSB7IHJldHVybiBpZWVlNzU0LnJlYWQodGhpcywgcG9zLCB0cnVlLCA1MiwgOCk7IH0sXG5cbiAgICB3cml0ZUZsb2F0TEU6ICBmdW5jdGlvbih2YWwsIHBvcykgeyByZXR1cm4gaWVlZTc1NC53cml0ZSh0aGlzLCB2YWwsIHBvcywgdHJ1ZSwgMjMsIDQpOyB9LFxuICAgIHdyaXRlRG91YmxlTEU6IGZ1bmN0aW9uKHZhbCwgcG9zKSB7IHJldHVybiBpZWVlNzU0LndyaXRlKHRoaXMsIHZhbCwgcG9zLCB0cnVlLCA1MiwgOCk7IH0sXG5cbiAgICB0b1N0cmluZzogZnVuY3Rpb24oZW5jb2RpbmcsIHN0YXJ0LCBlbmQpIHtcbiAgICAgICAgdmFyIHN0ciA9ICcnLFxuICAgICAgICAgICAgdG1wID0gJyc7XG5cbiAgICAgICAgc3RhcnQgPSBzdGFydCB8fCAwO1xuICAgICAgICBlbmQgPSBNYXRoLm1pbih0aGlzLmxlbmd0aCwgZW5kIHx8IHRoaXMubGVuZ3RoKTtcblxuICAgICAgICBmb3IgKHZhciBpID0gc3RhcnQ7IGkgPCBlbmQ7IGkrKykge1xuICAgICAgICAgICAgdmFyIGNoID0gdGhpc1tpXTtcbiAgICAgICAgICAgIGlmIChjaCA8PSAweDdGKSB7XG4gICAgICAgICAgICAgICAgc3RyICs9IGRlY29kZVVSSUNvbXBvbmVudCh0bXApICsgU3RyaW5nLmZyb21DaGFyQ29kZShjaCk7XG4gICAgICAgICAgICAgICAgdG1wID0gJyc7XG4gICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgIHRtcCArPSAnJScgKyBjaC50b1N0cmluZygxNik7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cblxuICAgICAgICBzdHIgKz0gZGVjb2RlVVJJQ29tcG9uZW50KHRtcCk7XG5cbiAgICAgICAgcmV0dXJuIHN0cjtcbiAgICB9LFxuXG4gICAgd3JpdGU6IGZ1bmN0aW9uKHN0ciwgcG9zKSB7XG4gICAgICAgIHZhciBieXRlcyA9IHN0ciA9PT0gbGFzdFN0ciA/IGxhc3RTdHJFbmNvZGVkIDogZW5jb2RlU3RyaW5nKHN0cik7XG4gICAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgYnl0ZXMubGVuZ3RoOyBpKyspIHtcbiAgICAgICAgICAgIHRoaXNbcG9zICsgaV0gPSBieXRlc1tpXTtcbiAgICAgICAgfVxuICAgIH0sXG5cbiAgICBzbGljZTogZnVuY3Rpb24oc3RhcnQsIGVuZCkge1xuICAgICAgICByZXR1cm4gdGhpcy5zdWJhcnJheShzdGFydCwgZW5kKTtcbiAgICB9LFxuXG4gICAgY29weTogZnVuY3Rpb24oYnVmLCBwb3MpIHtcbiAgICAgICAgcG9zID0gcG9zIHx8IDA7XG4gICAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgdGhpcy5sZW5ndGg7IGkrKykge1xuICAgICAgICAgICAgYnVmW3BvcyArIGldID0gdGhpc1tpXTtcbiAgICAgICAgfVxuICAgIH1cbn07XG5cbkJ1ZmZlck1ldGhvZHMud3JpdGVJbnQzMkxFID0gQnVmZmVyTWV0aG9kcy53cml0ZVVJbnQzMkxFO1xuXG5CdWZmZXIuYnl0ZUxlbmd0aCA9IGZ1bmN0aW9uKHN0cikge1xuICAgIGxhc3RTdHIgPSBzdHI7XG4gICAgbGFzdFN0ckVuY29kZWQgPSBlbmNvZGVTdHJpbmcoc3RyKTtcbiAgICByZXR1cm4gbGFzdFN0ckVuY29kZWQubGVuZ3RoO1xufTtcblxuQnVmZmVyLmlzQnVmZmVyID0gZnVuY3Rpb24oYnVmKSB7XG4gICAgcmV0dXJuICEhKGJ1ZiAmJiBidWYuX2lzQnVmZmVyKTtcbn07XG5cbmZ1bmN0aW9uIGVuY29kZVN0cmluZyhzdHIpIHtcbiAgICB2YXIgbGVuZ3RoID0gc3RyLmxlbmd0aCxcbiAgICAgICAgYnl0ZXMgPSBbXTtcblxuICAgIGZvciAodmFyIGkgPSAwLCBjLCBsZWFkOyBpIDwgbGVuZ3RoOyBpKyspIHtcbiAgICAgICAgYyA9IHN0ci5jaGFyQ29kZUF0KGkpOyAvLyBjb2RlIHBvaW50XG5cbiAgICAgICAgaWYgKGMgPiAweEQ3RkYgJiYgYyA8IDB4RTAwMCkge1xuXG4gICAgICAgICAgICBpZiAobGVhZCkge1xuICAgICAgICAgICAgICAgIGlmIChjIDwgMHhEQzAwKSB7XG4gICAgICAgICAgICAgICAgICAgIGJ5dGVzLnB1c2goMHhFRiwgMHhCRiwgMHhCRCk7XG4gICAgICAgICAgICAgICAgICAgIGxlYWQgPSBjO1xuICAgICAgICAgICAgICAgICAgICBjb250aW51ZTtcblxuICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgIGMgPSBsZWFkIC0gMHhEODAwIDw8IDEwIHwgYyAtIDB4REMwMCB8IDB4MTAwMDA7XG4gICAgICAgICAgICAgICAgICAgIGxlYWQgPSBudWxsO1xuICAgICAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICBpZiAoYyA+IDB4REJGRiB8fCAoaSArIDEgPT09IGxlbmd0aCkpIGJ5dGVzLnB1c2goMHhFRiwgMHhCRiwgMHhCRCk7XG4gICAgICAgICAgICAgICAgZWxzZSBsZWFkID0gYztcblxuICAgICAgICAgICAgICAgIGNvbnRpbnVlO1xuICAgICAgICAgICAgfVxuXG4gICAgICAgIH0gZWxzZSBpZiAobGVhZCkge1xuICAgICAgICAgICAgYnl0ZXMucHVzaCgweEVGLCAweEJGLCAweEJEKTtcbiAgICAgICAgICAgIGxlYWQgPSBudWxsO1xuICAgICAgICB9XG5cbiAgICAgICAgaWYgKGMgPCAweDgwKSBieXRlcy5wdXNoKGMpO1xuICAgICAgICBlbHNlIHtcbiAgICAgICAgICAgIGlmIChjIDwgMHg4MDApIGJ5dGVzLnB1c2goYyA+PiAweDYgfCAweEMwLCBjICYgMHgzRiB8IDB4ODApO1xuICAgICAgICAgICAgZWxzZSBpZiAoYyA8IDB4MTAwMDApIGJ5dGVzLnB1c2goYyA+PiAweEMgfCAweEUwLCBjID4+IDB4NiAmIDB4M0YgfCAweDgwLCBjICYgMHgzRiB8IDB4ODApO1xuICAgICAgICAgICAgZWxzZSBieXRlcy5wdXNoKGMgPj4gMHgxMiB8IDB4RjAsIGMgPj4gMHhDICYgMHgzRiB8IDB4ODAsIGMgPj4gMHg2ICYgMHgzRiB8IDB4ODAsIGMgJiAweDNGIHwgMHg4MCk7XG4gICAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIGJ5dGVzO1xufVxuIiwiJ3VzZSBzdHJpY3QnO1xuXG5tb2R1bGUuZXhwb3J0cyA9IFBiZjtcblxudmFyIEJ1ZmZlciA9IGdsb2JhbC5CdWZmZXIgfHwgcmVxdWlyZSgnLi9idWZmZXInKTtcblxuZnVuY3Rpb24gUGJmKGJ1Zikge1xuICAgIHRoaXMuYnVmID0gIUJ1ZmZlci5pc0J1ZmZlcihidWYpID8gbmV3IEJ1ZmZlcihidWYgfHwgMCkgOiBidWY7XG4gICAgdGhpcy5wb3MgPSAwO1xuICAgIHRoaXMubGVuZ3RoID0gdGhpcy5idWYubGVuZ3RoO1xufVxuXG5QYmYuVmFyaW50ICA9IDA7IC8vIHZhcmludDogaW50MzIsIGludDY0LCB1aW50MzIsIHVpbnQ2NCwgc2ludDMyLCBzaW50NjQsIGJvb2wsIGVudW1cblBiZi5GaXhlZDY0ID0gMTsgLy8gNjQtYml0OiBkb3VibGUsIGZpeGVkNjQsIHNmaXhlZDY0XG5QYmYuQnl0ZXMgICA9IDI7IC8vIGxlbmd0aC1kZWxpbWl0ZWQ6IHN0cmluZywgYnl0ZXMsIGVtYmVkZGVkIG1lc3NhZ2VzLCBwYWNrZWQgcmVwZWF0ZWQgZmllbGRzXG5QYmYuRml4ZWQzMiA9IDU7IC8vIDMyLWJpdDogZmxvYXQsIGZpeGVkMzIsIHNmaXhlZDMyXG5cbnZhciBTSElGVF9MRUZUXzMyID0gKDEgPDwgMTYpICogKDEgPDwgMTYpLFxuICAgIFNISUZUX1JJR0hUXzMyID0gMSAvIFNISUZUX0xFRlRfMzI7XG5cblBiZi5wcm90b3R5cGUgPSB7XG5cbiAgICBkZXN0cm95OiBmdW5jdGlvbigpIHtcbiAgICAgICAgdGhpcy5idWYgPSBudWxsO1xuICAgIH0sXG5cbiAgICAvLyA9PT0gUkVBRElORyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PVxuXG4gICAgcmVhZEZpZWxkczogZnVuY3Rpb24ocmVhZEZpZWxkLCByZXN1bHQsIGVuZCkge1xuICAgICAgICBlbmQgPSBlbmQgfHwgdGhpcy5sZW5ndGg7XG5cbiAgICAgICAgd2hpbGUgKHRoaXMucG9zIDwgZW5kKSB7XG4gICAgICAgICAgICB2YXIgdmFsID0gdGhpcy5yZWFkVmFyaW50KCksXG4gICAgICAgICAgICAgICAgdGFnID0gdmFsID4+IDMsXG4gICAgICAgICAgICAgICAgc3RhcnRQb3MgPSB0aGlzLnBvcztcblxuICAgICAgICAgICAgcmVhZEZpZWxkKHRhZywgcmVzdWx0LCB0aGlzKTtcblxuICAgICAgICAgICAgaWYgKHRoaXMucG9zID09PSBzdGFydFBvcykgdGhpcy5za2lwKHZhbCk7XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIHJlc3VsdDtcbiAgICB9LFxuXG4gICAgcmVhZE1lc3NhZ2U6IGZ1bmN0aW9uKHJlYWRGaWVsZCwgcmVzdWx0KSB7XG4gICAgICAgIHJldHVybiB0aGlzLnJlYWRGaWVsZHMocmVhZEZpZWxkLCByZXN1bHQsIHRoaXMucmVhZFZhcmludCgpICsgdGhpcy5wb3MpO1xuICAgIH0sXG5cbiAgICByZWFkRml4ZWQzMjogZnVuY3Rpb24oKSB7XG4gICAgICAgIHZhciB2YWwgPSB0aGlzLmJ1Zi5yZWFkVUludDMyTEUodGhpcy5wb3MpO1xuICAgICAgICB0aGlzLnBvcyArPSA0O1xuICAgICAgICByZXR1cm4gdmFsO1xuICAgIH0sXG5cbiAgICByZWFkU0ZpeGVkMzI6IGZ1bmN0aW9uKCkge1xuICAgICAgICB2YXIgdmFsID0gdGhpcy5idWYucmVhZEludDMyTEUodGhpcy5wb3MpO1xuICAgICAgICB0aGlzLnBvcyArPSA0O1xuICAgICAgICByZXR1cm4gdmFsO1xuICAgIH0sXG5cbiAgICAvLyA2NC1iaXQgaW50IGhhbmRsaW5nIGlzIGJhc2VkIG9uIGdpdGh1Yi5jb20vZHB3L25vZGUtYnVmZmVyLW1vcmUtaW50cyAoTUlULWxpY2Vuc2VkKVxuXG4gICAgcmVhZEZpeGVkNjQ6IGZ1bmN0aW9uKCkge1xuICAgICAgICB2YXIgdmFsID0gdGhpcy5idWYucmVhZFVJbnQzMkxFKHRoaXMucG9zKSArIHRoaXMuYnVmLnJlYWRVSW50MzJMRSh0aGlzLnBvcyArIDQpICogU0hJRlRfTEVGVF8zMjtcbiAgICAgICAgdGhpcy5wb3MgKz0gODtcbiAgICAgICAgcmV0dXJuIHZhbDtcbiAgICB9LFxuXG4gICAgcmVhZFNGaXhlZDY0OiBmdW5jdGlvbigpIHtcbiAgICAgICAgdmFyIHZhbCA9IHRoaXMuYnVmLnJlYWRVSW50MzJMRSh0aGlzLnBvcykgKyB0aGlzLmJ1Zi5yZWFkSW50MzJMRSh0aGlzLnBvcyArIDQpICogU0hJRlRfTEVGVF8zMjtcbiAgICAgICAgdGhpcy5wb3MgKz0gODtcbiAgICAgICAgcmV0dXJuIHZhbDtcbiAgICB9LFxuXG4gICAgcmVhZEZsb2F0OiBmdW5jdGlvbigpIHtcbiAgICAgICAgdmFyIHZhbCA9IHRoaXMuYnVmLnJlYWRGbG9hdExFKHRoaXMucG9zKTtcbiAgICAgICAgdGhpcy5wb3MgKz0gNDtcbiAgICAgICAgcmV0dXJuIHZhbDtcbiAgICB9LFxuXG4gICAgcmVhZERvdWJsZTogZnVuY3Rpb24oKSB7XG4gICAgICAgIHZhciB2YWwgPSB0aGlzLmJ1Zi5yZWFkRG91YmxlTEUodGhpcy5wb3MpO1xuICAgICAgICB0aGlzLnBvcyArPSA4O1xuICAgICAgICByZXR1cm4gdmFsO1xuICAgIH0sXG5cbiAgICByZWFkVmFyaW50OiBmdW5jdGlvbigpIHtcbiAgICAgICAgdmFyIGJ1ZiA9IHRoaXMuYnVmLFxuICAgICAgICAgICAgdmFsLCBiLCBiMCwgYjEsIGIyLCBiMztcblxuICAgICAgICBiMCA9IGJ1Zlt0aGlzLnBvcysrXTsgaWYgKGIwIDwgMHg4MCkgcmV0dXJuIGIwOyAgICAgICAgICAgICAgICAgYjAgPSBiMCAmIDB4N2Y7XG4gICAgICAgIGIxID0gYnVmW3RoaXMucG9zKytdOyBpZiAoYjEgPCAweDgwKSByZXR1cm4gYjAgfCBiMSA8PCA3OyAgICAgICBiMSA9IChiMSAmIDB4N2YpIDw8IDc7XG4gICAgICAgIGIyID0gYnVmW3RoaXMucG9zKytdOyBpZiAoYjIgPCAweDgwKSByZXR1cm4gYjAgfCBiMSB8IGIyIDw8IDE0OyBiMiA9IChiMiAmIDB4N2YpIDw8IDE0O1xuICAgICAgICBiMyA9IGJ1Zlt0aGlzLnBvcysrXTsgaWYgKGIzIDwgMHg4MCkgcmV0dXJuIGIwIHwgYjEgfCBiMiB8IGIzIDw8IDIxO1xuXG4gICAgICAgIHZhbCA9IGIwIHwgYjEgfCBiMiB8IChiMyAmIDB4N2YpIDw8IDIxO1xuXG4gICAgICAgIGIgPSBidWZbdGhpcy5wb3MrK107IHZhbCArPSAoYiAmIDB4N2YpICogMHgxMDAwMDAwMDsgICAgICAgICBpZiAoYiA8IDB4ODApIHJldHVybiB2YWw7XG4gICAgICAgIGIgPSBidWZbdGhpcy5wb3MrK107IHZhbCArPSAoYiAmIDB4N2YpICogMHg4MDAwMDAwMDA7ICAgICAgICBpZiAoYiA8IDB4ODApIHJldHVybiB2YWw7XG4gICAgICAgIGIgPSBidWZbdGhpcy5wb3MrK107IHZhbCArPSAoYiAmIDB4N2YpICogMHg0MDAwMDAwMDAwMDsgICAgICBpZiAoYiA8IDB4ODApIHJldHVybiB2YWw7XG4gICAgICAgIGIgPSBidWZbdGhpcy5wb3MrK107IHZhbCArPSAoYiAmIDB4N2YpICogMHgyMDAwMDAwMDAwMDAwOyAgICBpZiAoYiA8IDB4ODApIHJldHVybiB2YWw7XG4gICAgICAgIGIgPSBidWZbdGhpcy5wb3MrK107IHZhbCArPSAoYiAmIDB4N2YpICogMHgxMDAwMDAwMDAwMDAwMDA7ICBpZiAoYiA8IDB4ODApIHJldHVybiB2YWw7XG4gICAgICAgIGIgPSBidWZbdGhpcy5wb3MrK107IHZhbCArPSAoYiAmIDB4N2YpICogMHg4MDAwMDAwMDAwMDAwMDAwOyBpZiAoYiA8IDB4ODApIHJldHVybiB2YWw7XG5cbiAgICAgICAgdGhyb3cgbmV3IEVycm9yKCdFeHBlY3RlZCB2YXJpbnQgbm90IG1vcmUgdGhhbiAxMCBieXRlcycpO1xuICAgIH0sXG5cbiAgICByZWFkU1ZhcmludDogZnVuY3Rpb24oKSB7XG4gICAgICAgIHZhciBudW0gPSB0aGlzLnJlYWRWYXJpbnQoKTtcbiAgICAgICAgcmV0dXJuIG51bSAlIDIgPT09IDEgPyAobnVtICsgMSkgLyAtMiA6IG51bSAvIDI7IC8vIHppZ3phZyBlbmNvZGluZ1xuICAgIH0sXG5cbiAgICByZWFkQm9vbGVhbjogZnVuY3Rpb24oKSB7XG4gICAgICAgIHJldHVybiBCb29sZWFuKHRoaXMucmVhZFZhcmludCgpKTtcbiAgICB9LFxuXG4gICAgcmVhZFN0cmluZzogZnVuY3Rpb24oKSB7XG4gICAgICAgIHZhciBlbmQgPSB0aGlzLnJlYWRWYXJpbnQoKSArIHRoaXMucG9zLFxuICAgICAgICAgICAgc3RyID0gdGhpcy5idWYudG9TdHJpbmcoJ3V0ZjgnLCB0aGlzLnBvcywgZW5kKTtcbiAgICAgICAgdGhpcy5wb3MgPSBlbmQ7XG4gICAgICAgIHJldHVybiBzdHI7XG4gICAgfSxcblxuICAgIHJlYWRCeXRlczogZnVuY3Rpb24oKSB7XG4gICAgICAgIHZhciBlbmQgPSB0aGlzLnJlYWRWYXJpbnQoKSArIHRoaXMucG9zLFxuICAgICAgICAgICAgYnVmZmVyID0gdGhpcy5idWYuc2xpY2UodGhpcy5wb3MsIGVuZCk7XG4gICAgICAgIHRoaXMucG9zID0gZW5kO1xuICAgICAgICByZXR1cm4gYnVmZmVyO1xuICAgIH0sXG5cbiAgICAvLyB2ZXJib3NlIGZvciBwZXJmb3JtYW5jZSByZWFzb25zOyBkb2Vzbid0IGFmZmVjdCBnemlwcGVkIHNpemVcblxuICAgIHJlYWRQYWNrZWRWYXJpbnQ6IGZ1bmN0aW9uKCkge1xuICAgICAgICB2YXIgZW5kID0gdGhpcy5yZWFkVmFyaW50KCkgKyB0aGlzLnBvcywgYXJyID0gW107XG4gICAgICAgIHdoaWxlICh0aGlzLnBvcyA8IGVuZCkgYXJyLnB1c2godGhpcy5yZWFkVmFyaW50KCkpO1xuICAgICAgICByZXR1cm4gYXJyO1xuICAgIH0sXG4gICAgcmVhZFBhY2tlZFNWYXJpbnQ6IGZ1bmN0aW9uKCkge1xuICAgICAgICB2YXIgZW5kID0gdGhpcy5yZWFkVmFyaW50KCkgKyB0aGlzLnBvcywgYXJyID0gW107XG4gICAgICAgIHdoaWxlICh0aGlzLnBvcyA8IGVuZCkgYXJyLnB1c2godGhpcy5yZWFkU1ZhcmludCgpKTtcbiAgICAgICAgcmV0dXJuIGFycjtcbiAgICB9LFxuICAgIHJlYWRQYWNrZWRCb29sZWFuOiBmdW5jdGlvbigpIHtcbiAgICAgICAgdmFyIGVuZCA9IHRoaXMucmVhZFZhcmludCgpICsgdGhpcy5wb3MsIGFyciA9IFtdO1xuICAgICAgICB3aGlsZSAodGhpcy5wb3MgPCBlbmQpIGFyci5wdXNoKHRoaXMucmVhZEJvb2xlYW4oKSk7XG4gICAgICAgIHJldHVybiBhcnI7XG4gICAgfSxcbiAgICByZWFkUGFja2VkRmxvYXQ6IGZ1bmN0aW9uKCkge1xuICAgICAgICB2YXIgZW5kID0gdGhpcy5yZWFkVmFyaW50KCkgKyB0aGlzLnBvcywgYXJyID0gW107XG4gICAgICAgIHdoaWxlICh0aGlzLnBvcyA8IGVuZCkgYXJyLnB1c2godGhpcy5yZWFkRmxvYXQoKSk7XG4gICAgICAgIHJldHVybiBhcnI7XG4gICAgfSxcbiAgICByZWFkUGFja2VkRG91YmxlOiBmdW5jdGlvbigpIHtcbiAgICAgICAgdmFyIGVuZCA9IHRoaXMucmVhZFZhcmludCgpICsgdGhpcy5wb3MsIGFyciA9IFtdO1xuICAgICAgICB3aGlsZSAodGhpcy5wb3MgPCBlbmQpIGFyci5wdXNoKHRoaXMucmVhZERvdWJsZSgpKTtcbiAgICAgICAgcmV0dXJuIGFycjtcbiAgICB9LFxuICAgIHJlYWRQYWNrZWRGaXhlZDMyOiBmdW5jdGlvbigpIHtcbiAgICAgICAgdmFyIGVuZCA9IHRoaXMucmVhZFZhcmludCgpICsgdGhpcy5wb3MsIGFyciA9IFtdO1xuICAgICAgICB3aGlsZSAodGhpcy5wb3MgPCBlbmQpIGFyci5wdXNoKHRoaXMucmVhZEZpeGVkMzIoKSk7XG4gICAgICAgIHJldHVybiBhcnI7XG4gICAgfSxcbiAgICByZWFkUGFja2VkU0ZpeGVkMzI6IGZ1bmN0aW9uKCkge1xuICAgICAgICB2YXIgZW5kID0gdGhpcy5yZWFkVmFyaW50KCkgKyB0aGlzLnBvcywgYXJyID0gW107XG4gICAgICAgIHdoaWxlICh0aGlzLnBvcyA8IGVuZCkgYXJyLnB1c2godGhpcy5yZWFkU0ZpeGVkMzIoKSk7XG4gICAgICAgIHJldHVybiBhcnI7XG4gICAgfSxcbiAgICByZWFkUGFja2VkRml4ZWQ2NDogZnVuY3Rpb24oKSB7XG4gICAgICAgIHZhciBlbmQgPSB0aGlzLnJlYWRWYXJpbnQoKSArIHRoaXMucG9zLCBhcnIgPSBbXTtcbiAgICAgICAgd2hpbGUgKHRoaXMucG9zIDwgZW5kKSBhcnIucHVzaCh0aGlzLnJlYWRGaXhlZDY0KCkpO1xuICAgICAgICByZXR1cm4gYXJyO1xuICAgIH0sXG4gICAgcmVhZFBhY2tlZFNGaXhlZDY0OiBmdW5jdGlvbigpIHtcbiAgICAgICAgdmFyIGVuZCA9IHRoaXMucmVhZFZhcmludCgpICsgdGhpcy5wb3MsIGFyciA9IFtdO1xuICAgICAgICB3aGlsZSAodGhpcy5wb3MgPCBlbmQpIGFyci5wdXNoKHRoaXMucmVhZFNGaXhlZDY0KCkpO1xuICAgICAgICByZXR1cm4gYXJyO1xuICAgIH0sXG5cbiAgICBza2lwOiBmdW5jdGlvbih2YWwpIHtcbiAgICAgICAgdmFyIHR5cGUgPSB2YWwgJiAweDc7XG4gICAgICAgIGlmICh0eXBlID09PSBQYmYuVmFyaW50KSB3aGlsZSAodGhpcy5idWZbdGhpcy5wb3MrK10gPiAweDdmKTtcbiAgICAgICAgZWxzZSBpZiAodHlwZSA9PT0gUGJmLkJ5dGVzKSB0aGlzLnBvcyA9IHRoaXMucmVhZFZhcmludCgpICsgdGhpcy5wb3M7XG4gICAgICAgIGVsc2UgaWYgKHR5cGUgPT09IFBiZi5GaXhlZDMyKSB0aGlzLnBvcyArPSA0O1xuICAgICAgICBlbHNlIGlmICh0eXBlID09PSBQYmYuRml4ZWQ2NCkgdGhpcy5wb3MgKz0gODtcbiAgICAgICAgZWxzZSB0aHJvdyBuZXcgRXJyb3IoJ1VuaW1wbGVtZW50ZWQgdHlwZTogJyArIHR5cGUpO1xuICAgIH0sXG5cbiAgICAvLyA9PT0gV1JJVElORyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PVxuXG4gICAgd3JpdGVUYWc6IGZ1bmN0aW9uKHRhZywgdHlwZSkge1xuICAgICAgICB0aGlzLndyaXRlVmFyaW50KCh0YWcgPDwgMykgfCB0eXBlKTtcbiAgICB9LFxuXG4gICAgcmVhbGxvYzogZnVuY3Rpb24obWluKSB7XG4gICAgICAgIHZhciBsZW5ndGggPSB0aGlzLmxlbmd0aCB8fCAxNjtcblxuICAgICAgICB3aGlsZSAobGVuZ3RoIDwgdGhpcy5wb3MgKyBtaW4pIGxlbmd0aCAqPSAyO1xuXG4gICAgICAgIGlmIChsZW5ndGggIT0gdGhpcy5sZW5ndGgpIHtcbiAgICAgICAgICAgIHZhciBidWYgPSBuZXcgQnVmZmVyKGxlbmd0aCk7XG4gICAgICAgICAgICB0aGlzLmJ1Zi5jb3B5KGJ1Zik7XG4gICAgICAgICAgICB0aGlzLmJ1ZiA9IGJ1ZjtcbiAgICAgICAgICAgIHRoaXMubGVuZ3RoID0gbGVuZ3RoO1xuICAgICAgICB9XG4gICAgfSxcblxuICAgIGZpbmlzaDogZnVuY3Rpb24oKSB7XG4gICAgICAgIHRoaXMubGVuZ3RoID0gdGhpcy5wb3M7XG4gICAgICAgIHRoaXMucG9zID0gMDtcbiAgICAgICAgcmV0dXJuIHRoaXMuYnVmLnNsaWNlKDAsIHRoaXMubGVuZ3RoKTtcbiAgICB9LFxuXG4gICAgd3JpdGVGaXhlZDMyOiBmdW5jdGlvbih2YWwpIHtcbiAgICAgICAgdGhpcy5yZWFsbG9jKDQpO1xuICAgICAgICB0aGlzLmJ1Zi53cml0ZVVJbnQzMkxFKHZhbCwgdGhpcy5wb3MpO1xuICAgICAgICB0aGlzLnBvcyArPSA0O1xuICAgIH0sXG5cbiAgICB3cml0ZVNGaXhlZDMyOiBmdW5jdGlvbih2YWwpIHtcbiAgICAgICAgdGhpcy5yZWFsbG9jKDQpO1xuICAgICAgICB0aGlzLmJ1Zi53cml0ZUludDMyTEUodmFsLCB0aGlzLnBvcyk7XG4gICAgICAgIHRoaXMucG9zICs9IDQ7XG4gICAgfSxcblxuICAgIHdyaXRlRml4ZWQ2NDogZnVuY3Rpb24odmFsKSB7XG4gICAgICAgIHRoaXMucmVhbGxvYyg4KTtcbiAgICAgICAgdGhpcy5idWYud3JpdGVJbnQzMkxFKHZhbCAmIC0xLCB0aGlzLnBvcyk7XG4gICAgICAgIHRoaXMuYnVmLndyaXRlVUludDMyTEUoTWF0aC5mbG9vcih2YWwgKiBTSElGVF9SSUdIVF8zMiksIHRoaXMucG9zICsgNCk7XG4gICAgICAgIHRoaXMucG9zICs9IDg7XG4gICAgfSxcblxuICAgIHdyaXRlU0ZpeGVkNjQ6IGZ1bmN0aW9uKHZhbCkge1xuICAgICAgICB0aGlzLnJlYWxsb2MoOCk7XG4gICAgICAgIHRoaXMuYnVmLndyaXRlSW50MzJMRSh2YWwgJiAtMSwgdGhpcy5wb3MpO1xuICAgICAgICB0aGlzLmJ1Zi53cml0ZUludDMyTEUoTWF0aC5mbG9vcih2YWwgKiBTSElGVF9SSUdIVF8zMiksIHRoaXMucG9zICsgNCk7XG4gICAgICAgIHRoaXMucG9zICs9IDg7XG4gICAgfSxcblxuICAgIHdyaXRlVmFyaW50OiBmdW5jdGlvbih2YWwpIHtcbiAgICAgICAgdmFsID0gK3ZhbDtcblxuICAgICAgICBpZiAodmFsIDw9IDB4N2YpIHtcbiAgICAgICAgICAgIHRoaXMucmVhbGxvYygxKTtcbiAgICAgICAgICAgIHRoaXMuYnVmW3RoaXMucG9zKytdID0gdmFsO1xuXG4gICAgICAgIH0gZWxzZSBpZiAodmFsIDw9IDB4M2ZmZikge1xuICAgICAgICAgICAgdGhpcy5yZWFsbG9jKDIpO1xuICAgICAgICAgICAgdGhpcy5idWZbdGhpcy5wb3MrK10gPSAoKHZhbCA+Pj4gMCkgJiAweDdmKSB8IDB4ODA7XG4gICAgICAgICAgICB0aGlzLmJ1Zlt0aGlzLnBvcysrXSA9ICAodmFsID4+PiA3KSAmIDB4N2Y7XG5cbiAgICAgICAgfSBlbHNlIGlmICh2YWwgPD0gMHgxZmZmZmYpIHtcbiAgICAgICAgICAgIHRoaXMucmVhbGxvYygzKTtcbiAgICAgICAgICAgIHRoaXMuYnVmW3RoaXMucG9zKytdID0gKCh2YWwgPj4+ICAwKSAmIDB4N2YpIHwgMHg4MDtcbiAgICAgICAgICAgIHRoaXMuYnVmW3RoaXMucG9zKytdID0gKCh2YWwgPj4+ICA3KSAmIDB4N2YpIHwgMHg4MDtcbiAgICAgICAgICAgIHRoaXMuYnVmW3RoaXMucG9zKytdID0gICh2YWwgPj4+IDE0KSAmIDB4N2Y7XG5cbiAgICAgICAgfSBlbHNlIGlmICh2YWwgPD0gMHhmZmZmZmZmKSB7XG4gICAgICAgICAgICB0aGlzLnJlYWxsb2MoNCk7XG4gICAgICAgICAgICB0aGlzLmJ1Zlt0aGlzLnBvcysrXSA9ICgodmFsID4+PiAgMCkgJiAweDdmKSB8IDB4ODA7XG4gICAgICAgICAgICB0aGlzLmJ1Zlt0aGlzLnBvcysrXSA9ICgodmFsID4+PiAgNykgJiAweDdmKSB8IDB4ODA7XG4gICAgICAgICAgICB0aGlzLmJ1Zlt0aGlzLnBvcysrXSA9ICgodmFsID4+PiAxNCkgJiAweDdmKSB8IDB4ODA7XG4gICAgICAgICAgICB0aGlzLmJ1Zlt0aGlzLnBvcysrXSA9ICAodmFsID4+PiAyMSkgJiAweDdmO1xuXG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICB2YXIgcG9zID0gdGhpcy5wb3M7XG4gICAgICAgICAgICB3aGlsZSAodmFsID49IDB4ODApIHtcbiAgICAgICAgICAgICAgICB0aGlzLnJlYWxsb2MoMSk7XG4gICAgICAgICAgICAgICAgdGhpcy5idWZbdGhpcy5wb3MrK10gPSAodmFsICYgMHhmZikgfCAweDgwO1xuICAgICAgICAgICAgICAgIHZhbCAvPSAweDgwO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgdGhpcy5yZWFsbG9jKDEpO1xuICAgICAgICAgICAgdGhpcy5idWZbdGhpcy5wb3MrK10gPSB2YWwgfCAwO1xuICAgICAgICAgICAgaWYgKHRoaXMucG9zIC0gcG9zID4gMTApIHRocm93IG5ldyBFcnJvcihcIkdpdmVuIHZhcmludCBkb2Vzbid0IGZpdCBpbnRvIDEwIGJ5dGVzXCIpO1xuICAgICAgICB9XG4gICAgfSxcblxuICAgIHdyaXRlU1ZhcmludDogZnVuY3Rpb24odmFsKSB7XG4gICAgICAgIHRoaXMud3JpdGVWYXJpbnQodmFsIDwgMCA/IC12YWwgKiAyIC0gMSA6IHZhbCAqIDIpO1xuICAgIH0sXG5cbiAgICB3cml0ZUJvb2xlYW46IGZ1bmN0aW9uKHZhbCkge1xuICAgICAgICB0aGlzLndyaXRlVmFyaW50KEJvb2xlYW4odmFsKSk7XG4gICAgfSxcblxuICAgIHdyaXRlU3RyaW5nOiBmdW5jdGlvbihzdHIpIHtcbiAgICAgICAgc3RyID0gU3RyaW5nKHN0cik7XG4gICAgICAgIHZhciBieXRlcyA9IEJ1ZmZlci5ieXRlTGVuZ3RoKHN0cik7XG4gICAgICAgIHRoaXMud3JpdGVWYXJpbnQoYnl0ZXMpO1xuICAgICAgICB0aGlzLnJlYWxsb2MoYnl0ZXMpO1xuICAgICAgICB0aGlzLmJ1Zi53cml0ZShzdHIsIHRoaXMucG9zKTtcbiAgICAgICAgdGhpcy5wb3MgKz0gYnl0ZXM7XG4gICAgfSxcblxuICAgIHdyaXRlRmxvYXQ6IGZ1bmN0aW9uKHZhbCkge1xuICAgICAgICB0aGlzLnJlYWxsb2MoNCk7XG4gICAgICAgIHRoaXMuYnVmLndyaXRlRmxvYXRMRSh2YWwsIHRoaXMucG9zKTtcbiAgICAgICAgdGhpcy5wb3MgKz0gNDtcbiAgICB9LFxuXG4gICAgd3JpdGVEb3VibGU6IGZ1bmN0aW9uKHZhbCkge1xuICAgICAgICB0aGlzLnJlYWxsb2MoOCk7XG4gICAgICAgIHRoaXMuYnVmLndyaXRlRG91YmxlTEUodmFsLCB0aGlzLnBvcyk7XG4gICAgICAgIHRoaXMucG9zICs9IDg7XG4gICAgfSxcblxuICAgIHdyaXRlQnl0ZXM6IGZ1bmN0aW9uKGJ1ZmZlcikge1xuICAgICAgICB2YXIgbGVuID0gYnVmZmVyLmxlbmd0aDtcbiAgICAgICAgdGhpcy53cml0ZVZhcmludChsZW4pO1xuICAgICAgICB0aGlzLnJlYWxsb2MobGVuKTtcbiAgICAgICAgZm9yICh2YXIgaSA9IDA7IGkgPCBsZW47IGkrKykgdGhpcy5idWZbdGhpcy5wb3MrK10gPSBidWZmZXJbaV07XG4gICAgfSxcblxuICAgIHdyaXRlTWVzc2FnZTogZnVuY3Rpb24odGFnLCBmbiwgb2JqKSB7XG4gICAgICAgIHRoaXMud3JpdGVUYWcodGFnLCBQYmYuQnl0ZXMpO1xuXG4gICAgICAgIHRoaXMucG9zKys7IC8vIHJlc2VydmUgMSBieXRlIGZvciBzaG9ydCBtZXNzYWdlIGxlbmd0aFxuXG4gICAgICAgIC8vIHdyaXRlIHRoZSBtZXNzYWdlIGRpcmVjdGx5IHRvIHRoZSBidWZmZXIgYW5kIHNlZSBob3cgbXVjaCB3YXMgd3JpdHRlblxuICAgICAgICB2YXIgc3RhcnRQb3MgPSB0aGlzLnBvcztcbiAgICAgICAgZm4ob2JqLCB0aGlzKTtcbiAgICAgICAgdmFyIGxlbiA9IHRoaXMucG9zIC0gc3RhcnRQb3M7XG5cbiAgICAgICAgdmFyIHZhcmludExlbiA9XG4gICAgICAgICAgICBsZW4gPD0gMHg3ZiA/IDEgOlxuICAgICAgICAgICAgbGVuIDw9IDB4M2ZmZiA/IDIgOlxuICAgICAgICAgICAgbGVuIDw9IDB4MWZmZmZmID8gMyA6XG4gICAgICAgICAgICBsZW4gPD0gMHhmZmZmZmZmID8gNCA6IE1hdGguY2VpbChNYXRoLmxvZyhsZW4pIC8gKE1hdGguTE4yICogNykpO1xuXG4gICAgICAgIC8vIGlmIDEgYnl0ZSBpc24ndCBlbm91Z2ggZm9yIGVuY29kaW5nIG1lc3NhZ2UgbGVuZ3RoLCBzaGlmdCB0aGUgZGF0YSB0byB0aGUgcmlnaHRcbiAgICAgICAgaWYgKHZhcmludExlbiA+IDEpIHtcbiAgICAgICAgICAgIHRoaXMucmVhbGxvYyh2YXJpbnRMZW4gLSAxKTtcbiAgICAgICAgICAgIGZvciAodmFyIGkgPSB0aGlzLnBvcyAtIDE7IGkgPj0gc3RhcnRQb3M7IGktLSkgdGhpcy5idWZbaSArIHZhcmludExlbiAtIDFdID0gdGhpcy5idWZbaV07XG4gICAgICAgIH1cblxuICAgICAgICAvLyBmaW5hbGx5LCB3cml0ZSB0aGUgbWVzc2FnZSBsZW5ndGggaW4gdGhlIHJlc2VydmVkIHBsYWNlIGFuZCByZXN0b3JlIHRoZSBwb3NpdGlvblxuICAgICAgICB0aGlzLnBvcyA9IHN0YXJ0UG9zIC0gMTtcbiAgICAgICAgdGhpcy53cml0ZVZhcmludChsZW4pO1xuICAgICAgICB0aGlzLnBvcyArPSBsZW47XG4gICAgfSxcblxuICAgIHdyaXRlUGFja2VkVmFyaW50OiAgIGZ1bmN0aW9uKHRhZywgYXJyKSB7IHRoaXMud3JpdGVNZXNzYWdlKHRhZywgd3JpdGVQYWNrZWRWYXJpbnQsIGFycik7ICAgfSxcbiAgICB3cml0ZVBhY2tlZFNWYXJpbnQ6ICBmdW5jdGlvbih0YWcsIGFycikgeyB0aGlzLndyaXRlTWVzc2FnZSh0YWcsIHdyaXRlUGFja2VkU1ZhcmludCwgYXJyKTsgIH0sXG4gICAgd3JpdGVQYWNrZWRCb29sZWFuOiAgZnVuY3Rpb24odGFnLCBhcnIpIHsgdGhpcy53cml0ZU1lc3NhZ2UodGFnLCB3cml0ZVBhY2tlZEJvb2xlYW4sIGFycik7ICB9LFxuICAgIHdyaXRlUGFja2VkRmxvYXQ6ICAgIGZ1bmN0aW9uKHRhZywgYXJyKSB7IHRoaXMud3JpdGVNZXNzYWdlKHRhZywgd3JpdGVQYWNrZWRGbG9hdCwgYXJyKTsgICAgfSxcbiAgICB3cml0ZVBhY2tlZERvdWJsZTogICBmdW5jdGlvbih0YWcsIGFycikgeyB0aGlzLndyaXRlTWVzc2FnZSh0YWcsIHdyaXRlUGFja2VkRG91YmxlLCBhcnIpOyAgIH0sXG4gICAgd3JpdGVQYWNrZWRGaXhlZDMyOiAgZnVuY3Rpb24odGFnLCBhcnIpIHsgdGhpcy53cml0ZU1lc3NhZ2UodGFnLCB3cml0ZVBhY2tlZEZpeGVkMzIsIGFycik7ICB9LFxuICAgIHdyaXRlUGFja2VkU0ZpeGVkMzI6IGZ1bmN0aW9uKHRhZywgYXJyKSB7IHRoaXMud3JpdGVNZXNzYWdlKHRhZywgd3JpdGVQYWNrZWRTRml4ZWQzMiwgYXJyKTsgfSxcbiAgICB3cml0ZVBhY2tlZEZpeGVkNjQ6ICBmdW5jdGlvbih0YWcsIGFycikgeyB0aGlzLndyaXRlTWVzc2FnZSh0YWcsIHdyaXRlUGFja2VkRml4ZWQ2NCwgYXJyKTsgIH0sXG4gICAgd3JpdGVQYWNrZWRTRml4ZWQ2NDogZnVuY3Rpb24odGFnLCBhcnIpIHsgdGhpcy53cml0ZU1lc3NhZ2UodGFnLCB3cml0ZVBhY2tlZFNGaXhlZDY0LCBhcnIpOyB9LFxuXG4gICAgd3JpdGVCeXRlc0ZpZWxkOiBmdW5jdGlvbih0YWcsIGJ1ZmZlcikge1xuICAgICAgICB0aGlzLndyaXRlVGFnKHRhZywgUGJmLkJ5dGVzKTtcbiAgICAgICAgdGhpcy53cml0ZUJ5dGVzKGJ1ZmZlcik7XG4gICAgfSxcbiAgICB3cml0ZUZpeGVkMzJGaWVsZDogZnVuY3Rpb24odGFnLCB2YWwpIHtcbiAgICAgICAgdGhpcy53cml0ZVRhZyh0YWcsIFBiZi5GaXhlZDMyKTtcbiAgICAgICAgdGhpcy53cml0ZUZpeGVkMzIodmFsKTtcbiAgICB9LFxuICAgIHdyaXRlU0ZpeGVkMzJGaWVsZDogZnVuY3Rpb24odGFnLCB2YWwpIHtcbiAgICAgICAgdGhpcy53cml0ZVRhZyh0YWcsIFBiZi5GaXhlZDMyKTtcbiAgICAgICAgdGhpcy53cml0ZVNGaXhlZDMyKHZhbCk7XG4gICAgfSxcbiAgICB3cml0ZUZpeGVkNjRGaWVsZDogZnVuY3Rpb24odGFnLCB2YWwpIHtcbiAgICAgICAgdGhpcy53cml0ZVRhZyh0YWcsIFBiZi5GaXhlZDY0KTtcbiAgICAgICAgdGhpcy53cml0ZUZpeGVkNjQodmFsKTtcbiAgICB9LFxuICAgIHdyaXRlU0ZpeGVkNjRGaWVsZDogZnVuY3Rpb24odGFnLCB2YWwpIHtcbiAgICAgICAgdGhpcy53cml0ZVRhZyh0YWcsIFBiZi5GaXhlZDY0KTtcbiAgICAgICAgdGhpcy53cml0ZVNGaXhlZDY0KHZhbCk7XG4gICAgfSxcbiAgICB3cml0ZVZhcmludEZpZWxkOiBmdW5jdGlvbih0YWcsIHZhbCkge1xuICAgICAgICB0aGlzLndyaXRlVGFnKHRhZywgUGJmLlZhcmludCk7XG4gICAgICAgIHRoaXMud3JpdGVWYXJpbnQodmFsKTtcbiAgICB9LFxuICAgIHdyaXRlU1ZhcmludEZpZWxkOiBmdW5jdGlvbih0YWcsIHZhbCkge1xuICAgICAgICB0aGlzLndyaXRlVGFnKHRhZywgUGJmLlZhcmludCk7XG4gICAgICAgIHRoaXMud3JpdGVTVmFyaW50KHZhbCk7XG4gICAgfSxcbiAgICB3cml0ZVN0cmluZ0ZpZWxkOiBmdW5jdGlvbih0YWcsIHN0cikge1xuICAgICAgICB0aGlzLndyaXRlVGFnKHRhZywgUGJmLkJ5dGVzKTtcbiAgICAgICAgdGhpcy53cml0ZVN0cmluZyhzdHIpO1xuICAgIH0sXG4gICAgd3JpdGVGbG9hdEZpZWxkOiBmdW5jdGlvbih0YWcsIHZhbCkge1xuICAgICAgICB0aGlzLndyaXRlVGFnKHRhZywgUGJmLkZpeGVkMzIpO1xuICAgICAgICB0aGlzLndyaXRlRmxvYXQodmFsKTtcbiAgICB9LFxuICAgIHdyaXRlRG91YmxlRmllbGQ6IGZ1bmN0aW9uKHRhZywgdmFsKSB7XG4gICAgICAgIHRoaXMud3JpdGVUYWcodGFnLCBQYmYuRml4ZWQ2NCk7XG4gICAgICAgIHRoaXMud3JpdGVEb3VibGUodmFsKTtcbiAgICB9LFxuICAgIHdyaXRlQm9vbGVhbkZpZWxkOiBmdW5jdGlvbih0YWcsIHZhbCkge1xuICAgICAgICB0aGlzLndyaXRlVmFyaW50RmllbGQodGFnLCBCb29sZWFuKHZhbCkpO1xuICAgIH1cbn07XG5cbmZ1bmN0aW9uIHdyaXRlUGFja2VkVmFyaW50KGFyciwgcGJmKSAgIHsgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZVZhcmludChhcnJbaV0pOyAgIH1cbmZ1bmN0aW9uIHdyaXRlUGFja2VkU1ZhcmludChhcnIsIHBiZikgIHsgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZVNWYXJpbnQoYXJyW2ldKTsgIH1cbmZ1bmN0aW9uIHdyaXRlUGFja2VkRmxvYXQoYXJyLCBwYmYpICAgIHsgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZUZsb2F0KGFycltpXSk7ICAgIH1cbmZ1bmN0aW9uIHdyaXRlUGFja2VkRG91YmxlKGFyciwgcGJmKSAgIHsgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZURvdWJsZShhcnJbaV0pOyAgIH1cbmZ1bmN0aW9uIHdyaXRlUGFja2VkQm9vbGVhbihhcnIsIHBiZikgIHsgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZUJvb2xlYW4oYXJyW2ldKTsgIH1cbmZ1bmN0aW9uIHdyaXRlUGFja2VkRml4ZWQzMihhcnIsIHBiZikgIHsgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZUZpeGVkMzIoYXJyW2ldKTsgIH1cbmZ1bmN0aW9uIHdyaXRlUGFja2VkU0ZpeGVkMzIoYXJyLCBwYmYpIHsgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZVNGaXhlZDMyKGFycltpXSk7IH1cbmZ1bmN0aW9uIHdyaXRlUGFja2VkRml4ZWQ2NChhcnIsIHBiZikgIHsgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZUZpeGVkNjQoYXJyW2ldKTsgIH1cbmZ1bmN0aW9uIHdyaXRlUGFja2VkU0ZpeGVkNjQoYXJyLCBwYmYpIHsgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIHBiZi53cml0ZVNGaXhlZDY0KGFycltpXSk7IH1cbiIsImV4cG9ydHMucmVhZCA9IGZ1bmN0aW9uKGJ1ZmZlciwgb2Zmc2V0LCBpc0xFLCBtTGVuLCBuQnl0ZXMpIHtcbiAgdmFyIGUsIG0sXG4gICAgICBlTGVuID0gbkJ5dGVzICogOCAtIG1MZW4gLSAxLFxuICAgICAgZU1heCA9ICgxIDw8IGVMZW4pIC0gMSxcbiAgICAgIGVCaWFzID0gZU1heCA+PiAxLFxuICAgICAgbkJpdHMgPSAtNyxcbiAgICAgIGkgPSBpc0xFID8gKG5CeXRlcyAtIDEpIDogMCxcbiAgICAgIGQgPSBpc0xFID8gLTEgOiAxLFxuICAgICAgcyA9IGJ1ZmZlcltvZmZzZXQgKyBpXTtcblxuICBpICs9IGQ7XG5cbiAgZSA9IHMgJiAoKDEgPDwgKC1uQml0cykpIC0gMSk7XG4gIHMgPj49ICgtbkJpdHMpO1xuICBuQml0cyArPSBlTGVuO1xuICBmb3IgKDsgbkJpdHMgPiAwOyBlID0gZSAqIDI1NiArIGJ1ZmZlcltvZmZzZXQgKyBpXSwgaSArPSBkLCBuQml0cyAtPSA4KTtcblxuICBtID0gZSAmICgoMSA8PCAoLW5CaXRzKSkgLSAxKTtcbiAgZSA+Pj0gKC1uQml0cyk7XG4gIG5CaXRzICs9IG1MZW47XG4gIGZvciAoOyBuQml0cyA+IDA7IG0gPSBtICogMjU2ICsgYnVmZmVyW29mZnNldCArIGldLCBpICs9IGQsIG5CaXRzIC09IDgpO1xuXG4gIGlmIChlID09PSAwKSB7XG4gICAgZSA9IDEgLSBlQmlhcztcbiAgfSBlbHNlIGlmIChlID09PSBlTWF4KSB7XG4gICAgcmV0dXJuIG0gPyBOYU4gOiAoKHMgPyAtMSA6IDEpICogSW5maW5pdHkpO1xuICB9IGVsc2Uge1xuICAgIG0gPSBtICsgTWF0aC5wb3coMiwgbUxlbik7XG4gICAgZSA9IGUgLSBlQmlhcztcbiAgfVxuICByZXR1cm4gKHMgPyAtMSA6IDEpICogbSAqIE1hdGgucG93KDIsIGUgLSBtTGVuKTtcbn07XG5cbmV4cG9ydHMud3JpdGUgPSBmdW5jdGlvbihidWZmZXIsIHZhbHVlLCBvZmZzZXQsIGlzTEUsIG1MZW4sIG5CeXRlcykge1xuICB2YXIgZSwgbSwgYyxcbiAgICAgIGVMZW4gPSBuQnl0ZXMgKiA4IC0gbUxlbiAtIDEsXG4gICAgICBlTWF4ID0gKDEgPDwgZUxlbikgLSAxLFxuICAgICAgZUJpYXMgPSBlTWF4ID4+IDEsXG4gICAgICBydCA9IChtTGVuID09PSAyMyA/IE1hdGgucG93KDIsIC0yNCkgLSBNYXRoLnBvdygyLCAtNzcpIDogMCksXG4gICAgICBpID0gaXNMRSA/IDAgOiAobkJ5dGVzIC0gMSksXG4gICAgICBkID0gaXNMRSA/IDEgOiAtMSxcbiAgICAgIHMgPSB2YWx1ZSA8IDAgfHwgKHZhbHVlID09PSAwICYmIDEgLyB2YWx1ZSA8IDApID8gMSA6IDA7XG5cbiAgdmFsdWUgPSBNYXRoLmFicyh2YWx1ZSk7XG5cbiAgaWYgKGlzTmFOKHZhbHVlKSB8fCB2YWx1ZSA9PT0gSW5maW5pdHkpIHtcbiAgICBtID0gaXNOYU4odmFsdWUpID8gMSA6IDA7XG4gICAgZSA9IGVNYXg7XG4gIH0gZWxzZSB7XG4gICAgZSA9IE1hdGguZmxvb3IoTWF0aC5sb2codmFsdWUpIC8gTWF0aC5MTjIpO1xuICAgIGlmICh2YWx1ZSAqIChjID0gTWF0aC5wb3coMiwgLWUpKSA8IDEpIHtcbiAgICAgIGUtLTtcbiAgICAgIGMgKj0gMjtcbiAgICB9XG4gICAgaWYgKGUgKyBlQmlhcyA+PSAxKSB7XG4gICAgICB2YWx1ZSArPSBydCAvIGM7XG4gICAgfSBlbHNlIHtcbiAgICAgIHZhbHVlICs9IHJ0ICogTWF0aC5wb3coMiwgMSAtIGVCaWFzKTtcbiAgICB9XG4gICAgaWYgKHZhbHVlICogYyA+PSAyKSB7XG4gICAgICBlKys7XG4gICAgICBjIC89IDI7XG4gICAgfVxuXG4gICAgaWYgKGUgKyBlQmlhcyA+PSBlTWF4KSB7XG4gICAgICBtID0gMDtcbiAgICAgIGUgPSBlTWF4O1xuICAgIH0gZWxzZSBpZiAoZSArIGVCaWFzID49IDEpIHtcbiAgICAgIG0gPSAodmFsdWUgKiBjIC0gMSkgKiBNYXRoLnBvdygyLCBtTGVuKTtcbiAgICAgIGUgPSBlICsgZUJpYXM7XG4gICAgfSBlbHNlIHtcbiAgICAgIG0gPSB2YWx1ZSAqIE1hdGgucG93KDIsIGVCaWFzIC0gMSkgKiBNYXRoLnBvdygyLCBtTGVuKTtcbiAgICAgIGUgPSAwO1xuICAgIH1cbiAgfVxuXG4gIGZvciAoOyBtTGVuID49IDg7IGJ1ZmZlcltvZmZzZXQgKyBpXSA9IG0gJiAweGZmLCBpICs9IGQsIG0gLz0gMjU2LCBtTGVuIC09IDgpO1xuXG4gIGUgPSAoZSA8PCBtTGVuKSB8IG07XG4gIGVMZW4gKz0gbUxlbjtcbiAgZm9yICg7IGVMZW4gPiAwOyBidWZmZXJbb2Zmc2V0ICsgaV0gPSBlICYgMHhmZiwgaSArPSBkLCBlIC89IDI1NiwgZUxlbiAtPSA4KTtcblxuICBidWZmZXJbb2Zmc2V0ICsgaSAtIGRdIHw9IHMgKiAxMjg7XG59O1xuIl19
