(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.Pbf = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

// lightweight Buffer shim for pbf browser build
// based on code from github.com/feross/buffer (MIT-licensed)

module.exports = Buffer;

var ieee754 = require('ieee754');

var BufferMethods;

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

BufferMethods = {
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
        else if (c < 0x800) bytes.push(c >> 0x6 | 0xC0, c & 0x3F | 0x80);
        else if (c < 0x10000) bytes.push(c >> 0xC | 0xE0, c >> 0x6 & 0x3F | 0x80, c & 0x3F | 0x80);
        else bytes.push(c >> 0x12 | 0xF0, c >> 0xC & 0x3F | 0x80, c >> 0x6 & 0x3F | 0x80, c & 0x3F | 0x80);
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
    SHIFT_RIGHT_32 = 1 / SHIFT_LEFT_32,
    POW_2_63 = Math.pow(2, 63);

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

    readVarint64: function() {
        var startPos = this.pos,
            val = this.readVarint();

        if (val < POW_2_63) return val;

        var pos = this.pos - 2;
        while (this.buf[pos] === 0xff) pos--;
        if (pos < startPos) pos = startPos;

        val = 0;
        for (var i = 0; i < pos - startPos + 1; i++) {
            var b = ~this.buf[startPos + i] & 0x7f;
            val += i < 4 ? b << i * 7 : b * Math.pow(2, i * 7);
        }

        return -val - 1;
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
        if (type === Pbf.Varint) while (this.buf[this.pos++] > 0x7f) {}
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

        if (length !== this.length) {
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
            this.buf[this.pos++] = ((val >>> 7) & 0x7f);

        } else if (val <= 0x1fffff) {
            this.realloc(3);
            this.buf[this.pos++] = ((val >>> 0) & 0x7f) | 0x80;
            this.buf[this.pos++] = ((val >>> 7) & 0x7f) | 0x80;
            this.buf[this.pos++] = ((val >>> 14) & 0x7f);

        } else if (val <= 0xfffffff) {
            this.realloc(4);
            this.buf[this.pos++] = ((val >>> 0) & 0x7f) | 0x80;
            this.buf[this.pos++] = ((val >>> 7) & 0x7f) | 0x80;
            this.buf[this.pos++] = ((val >>> 14) & 0x7f) | 0x80;
            this.buf[this.pos++] = ((val >>> 21) & 0x7f);

        } else {
            var pos = this.pos;
            while (val >= 0x80) {
                this.realloc(1);
                this.buf[this.pos++] = (val & 0xff) | 0x80;
                val /= 0x80;
            }
            this.realloc(1);
            this.buf[this.pos++] = val | 0;
            if (this.pos - pos > 10) throw new Error('Given varint doesn\'t fit into 10 bytes');
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

    writeRawMessage: function(fn, obj) {
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

    writeMessage: function(tag, fn, obj) {
        this.writeTag(tag, Pbf.Bytes);
        this.writeRawMessage(fn, obj);
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
exports.read = function (buffer, offset, isLE, mLen, nBytes) {
  var e, m
  var eLen = nBytes * 8 - mLen - 1
  var eMax = (1 << eLen) - 1
  var eBias = eMax >> 1
  var nBits = -7
  var i = isLE ? (nBytes - 1) : 0
  var d = isLE ? -1 : 1
  var s = buffer[offset + i]

  i += d

  e = s & ((1 << (-nBits)) - 1)
  s >>= (-nBits)
  nBits += eLen
  for (; nBits > 0; e = e * 256 + buffer[offset + i], i += d, nBits -= 8) {}

  m = e & ((1 << (-nBits)) - 1)
  e >>= (-nBits)
  nBits += mLen
  for (; nBits > 0; m = m * 256 + buffer[offset + i], i += d, nBits -= 8) {}

  if (e === 0) {
    e = 1 - eBias
  } else if (e === eMax) {
    return m ? NaN : ((s ? -1 : 1) * Infinity)
  } else {
    m = m + Math.pow(2, mLen)
    e = e - eBias
  }
  return (s ? -1 : 1) * m * Math.pow(2, e - mLen)
}

exports.write = function (buffer, value, offset, isLE, mLen, nBytes) {
  var e, m, c
  var eLen = nBytes * 8 - mLen - 1
  var eMax = (1 << eLen) - 1
  var eBias = eMax >> 1
  var rt = (mLen === 23 ? Math.pow(2, -24) - Math.pow(2, -77) : 0)
  var i = isLE ? 0 : (nBytes - 1)
  var d = isLE ? 1 : -1
  var s = value < 0 || (value === 0 && 1 / value < 0) ? 1 : 0

  value = Math.abs(value)

  if (isNaN(value) || value === Infinity) {
    m = isNaN(value) ? 1 : 0
    e = eMax
  } else {
    e = Math.floor(Math.log(value) / Math.LN2)
    if (value * (c = Math.pow(2, -e)) < 1) {
      e--
      c *= 2
    }
    if (e + eBias >= 1) {
      value += rt / c
    } else {
      value += rt * Math.pow(2, 1 - eBias)
    }
    if (value * c >= 2) {
      e++
      c /= 2
    }

    if (e + eBias >= eMax) {
      m = 0
      e = eMax
    } else if (e + eBias >= 1) {
      m = (value * c - 1) * Math.pow(2, mLen)
      e = e + eBias
    } else {
      m = value * Math.pow(2, eBias - 1) * Math.pow(2, mLen)
      e = 0
    }
  }

  for (; mLen >= 8; buffer[offset + i] = m & 0xff, i += d, m /= 256, mLen -= 8) {}

  e = (e << mLen) | m
  eLen += mLen
  for (; eLen > 0; buffer[offset + i] = e & 0xff, i += d, e /= 256, eLen -= 8) {}

  buffer[offset + i - d] |= s * 128
}

},{}]},{},[2])(2)
});


(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.vectorTile = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
module.exports.VectorTile = require('./lib/vectortile.js');
module.exports.VectorTileFeature = require('./lib/vectortilefeature.js');
module.exports.VectorTileLayer = require('./lib/vectortilelayer.js');

},{"./lib/vectortile.js":2,"./lib/vectortilefeature.js":3,"./lib/vectortilelayer.js":4}],2:[function(require,module,exports){
'use strict';

var VectorTileLayer = require('./vectortilelayer');

module.exports = VectorTile;

function VectorTile(pbf, end) {
    this.layers = pbf.readFields(readTile, {}, end);
}

function readTile(tag, layers, pbf) {
    if (tag === 3) {
        var layer = new VectorTileLayer(pbf, pbf.readVarint() + pbf.pos);
        if (layer.length) layers[layer.name] = layer;
    }
}


},{"./vectortilelayer":4}],3:[function(require,module,exports){
'use strict';

var Point = require('point-geometry');

module.exports = VectorTileFeature;

function VectorTileFeature(pbf, end, extent, keys, values) {
    // Public
    this.properties = {};
    this.extent = extent;
    this.type = 0;

    // Private
    this._pbf = pbf;
    this._geometry = -1;
    this._keys = keys;
    this._values = values;

    pbf.readFields(readFeature, this, end);
}

function readFeature(tag, feature, pbf) {
    if (tag == 1) feature._id = pbf.readVarint();
    else if (tag == 2) readTag(pbf, feature);
    else if (tag == 3) feature.type = pbf.readVarint();
    else if (tag == 4) feature._geometry = pbf.pos;
}

function readTag(pbf, feature) {
    var end = pbf.readVarint() + pbf.pos;

    while (pbf.pos < end) {
        var key = feature._keys[pbf.readVarint()],
            value = feature._values[pbf.readVarint()];
        feature.properties[key] = value;
    }
}

VectorTileFeature.types = ['Unknown', 'Point', 'LineString', 'Polygon'];

VectorTileFeature.prototype.loadGeometry = function() {
    var pbf = this._pbf;
    pbf.pos = this._geometry;

    var end = pbf.readVarint() + pbf.pos,
        cmd = 1,
        length = 0,
        x = 0,
        y = 0,
        lines = [],
        line;

    while (pbf.pos < end) {
        if (!length) {
            var cmdLen = pbf.readVarint();
            cmd = cmdLen & 0x7;
            length = cmdLen >> 3;
        }

        length--;

        if (cmd === 1 || cmd === 2) {
            x += pbf.readSVarint();
            y += pbf.readSVarint();

            if (cmd === 1) { // moveTo
                if (line) lines.push(line);
                line = [];
            }

            line.push(new Point(x, y));

        } else if (cmd === 7) {

            // Workaround for https://github.com/mapbox/mapnik-vector-tile/issues/90
            if (line) {
                line.push(line[0].clone()); // closePolygon
            }

        } else {
            throw new Error('unknown command ' + cmd);
        }
    }

    if (line) lines.push(line);

    return lines;
};

VectorTileFeature.prototype.bbox = function() {
    var pbf = this._pbf;
    pbf.pos = this._geometry;

    var end = pbf.readVarint() + pbf.pos,
        cmd = 1,
        length = 0,
        x = 0,
        y = 0,
        x1 = Infinity,
        x2 = -Infinity,
        y1 = Infinity,
        y2 = -Infinity;

    while (pbf.pos < end) {
        if (!length) {
            var cmdLen = pbf.readVarint();
            cmd = cmdLen & 0x7;
            length = cmdLen >> 3;
        }

        length--;

        if (cmd === 1 || cmd === 2) {
            x += pbf.readSVarint();
            y += pbf.readSVarint();
            if (x < x1) x1 = x;
            if (x > x2) x2 = x;
            if (y < y1) y1 = y;
            if (y > y2) y2 = y;

        } else if (cmd !== 7) {
            throw new Error('unknown command ' + cmd);
        }
    }

    return [x1, y1, x2, y2];
};

VectorTileFeature.prototype.toGeoJSON = function(x, y, z) {
    var size = this.extent * Math.pow(2, z),
        x0 = this.extent * x,
        y0 = this.extent * y,
        coords = this.loadGeometry(),
        type = VectorTileFeature.types[this.type];

    for (var i = 0; i < coords.length; i++) {
        var line = coords[i];
        for (var j = 0; j < line.length; j++) {
            var p = line[j], y2 = 180 - (p.y + y0) * 360 / size;
            line[j] = [
                (p.x + x0) * 360 / size - 180,
                360 / Math.PI * Math.atan(Math.exp(y2 * Math.PI / 180)) - 90
            ];
        }
    }

    if (type === 'Point' && coords.length === 1) {
        coords = coords[0][0];
    } else if (type === 'Point') {
        coords = coords[0];
        type = 'MultiPoint';
    } else if (type === 'LineString' && coords.length === 1) {
        coords = coords[0];
    } else if (type === 'LineString') {
        type = 'MultiLineString';
    }

    var result = {
        type: "Feature",
        geometry: {
            type: type,
            coordinates: coords
        },
        properties: this.properties
    };

    if ('_id' in this) {
        result.id = this._id;
    }

    return result;
};

},{"point-geometry":5}],4:[function(require,module,exports){
'use strict';

var VectorTileFeature = require('./vectortilefeature.js');

module.exports = VectorTileLayer;

function VectorTileLayer(pbf, end) {
    // Public
    this.version = 1;
    this.name = null;
    this.extent = 4096;
    this.length = 0;

    // Private
    this._pbf = pbf;
    this._keys = [];
    this._values = [];
    this._features = [];

    pbf.readFields(readLayer, this, end);

    this.length = this._features.length;
}

function readLayer(tag, layer, pbf) {
    if (tag === 15) layer.version = pbf.readVarint();
    else if (tag === 1) layer.name = pbf.readString();
    else if (tag === 5) layer.extent = pbf.readVarint();
    else if (tag === 2) layer._features.push(pbf.pos);
    else if (tag === 3) layer._keys.push(pbf.readString());
    else if (tag === 4) layer._values.push(readValueMessage(pbf));
}

function readValueMessage(pbf) {
    var value = null,
        end = pbf.readVarint() + pbf.pos;

    while (pbf.pos < end) {
        var tag = pbf.readVarint() >> 3;

        value = tag === 1 ? pbf.readString() :
            tag === 2 ? pbf.readFloat() :
            tag === 3 ? pbf.readDouble() :
            tag === 4 ? pbf.readVarint64() :
            tag === 5 ? pbf.readVarint() :
            tag === 6 ? pbf.readSVarint() :
            tag === 7 ? pbf.readBoolean() : null;
    }

    return value;
}

// return feature `i` from this layer as a `VectorTileFeature`
VectorTileLayer.prototype.feature = function(i) {
    if (i < 0 || i >= this._features.length) throw new Error('feature index out of bounds');

    this._pbf.pos = this._features[i];

    var end = this._pbf.readVarint() + this._pbf.pos;
    return new VectorTileFeature(this._pbf, end, this.extent, this._keys, this._values);
};

},{"./vectortilefeature.js":3}],5:[function(require,module,exports){
'use strict';

module.exports = Point;

function Point(x, y) {
    this.x = x;
    this.y = y;
}

Point.prototype = {
    clone: function() { return new Point(this.x, this.y); },

    add:     function(p) { return this.clone()._add(p);     },
    sub:     function(p) { return this.clone()._sub(p);     },
    mult:    function(k) { return this.clone()._mult(k);    },
    div:     function(k) { return this.clone()._div(k);     },
    rotate:  function(a) { return this.clone()._rotate(a);  },
    matMult: function(m) { return this.clone()._matMult(m); },
    unit:    function() { return this.clone()._unit(); },
    perp:    function() { return this.clone()._perp(); },
    round:   function() { return this.clone()._round(); },

    mag: function() {
        return Math.sqrt(this.x * this.x + this.y * this.y);
    },

    equals: function(p) {
        return this.x === p.x &&
               this.y === p.y;
    },

    dist: function(p) {
        return Math.sqrt(this.distSqr(p));
    },

    distSqr: function(p) {
        var dx = p.x - this.x,
            dy = p.y - this.y;
        return dx * dx + dy * dy;
    },

    angle: function() {
        return Math.atan2(this.y, this.x);
    },

    angleTo: function(b) {
        return Math.atan2(this.y - b.y, this.x - b.x);
    },

    angleWith: function(b) {
        return this.angleWithSep(b.x, b.y);
    },

    // Find the angle of the two vectors, solving the formula for the cross product a x b = |a||b|sin(θ) for θ.
    angleWithSep: function(x, y) {
        return Math.atan2(
            this.x * y - this.y * x,
            this.x * x + this.y * y);
    },

    _matMult: function(m) {
        var x = m[0] * this.x + m[1] * this.y,
            y = m[2] * this.x + m[3] * this.y;
        this.x = x;
        this.y = y;
        return this;
    },

    _add: function(p) {
        this.x += p.x;
        this.y += p.y;
        return this;
    },

    _sub: function(p) {
        this.x -= p.x;
        this.y -= p.y;
        return this;
    },

    _mult: function(k) {
        this.x *= k;
        this.y *= k;
        return this;
    },

    _div: function(k) {
        this.x /= k;
        this.y /= k;
        return this;
    },

    _unit: function() {
        this._div(this.mag());
        return this;
    },

    _perp: function() {
        var y = this.y;
        this.y = this.x;
        this.x = -y;
        return this;
    },

    _rotate: function(angle) {
        var cos = Math.cos(angle),
            sin = Math.sin(angle),
            x = cos * this.x - sin * this.y,
            y = sin * this.x + cos * this.y;
        this.x = x;
        this.y = y;
        return this;
    },

    _round: function() {
        this.x = Math.round(this.x);
        this.y = Math.round(this.y);
        return this;
    }
};

// constructs Point from an array if necessary
Point.convert = function (a) {
    if (a instanceof Point) {
        return a;
    }
    if (Array.isArray(a)) {
        return new Point(a[0], a[1]);
    }
    return a;
};

},{}]},{},[1])(1)
});





L.SVG.Tile = L.SVG.extend({

	initialize: function (tileSize, options) {
		L.SVG.prototype.initialize.call(this, options);
		this._size = tileSize;

		this._initContainer();
		this._container.setAttribute('width', this._size.x);
		this._container.setAttribute('height', this._size.y);
		this._container.setAttribute('viewBox', [0, 0, this._size.x, this._size.y].join(' '));
	},

	getContainer: function() {
		return this._container;
	},

// 	onAdd: function() {},
	onAdd: L.Util.FalseFn,

	_initContainer: function() {
		L.SVG.prototype._initContainer.call(this);
		var rect =  L.SVG.create('rect');

// 		rect.setAttribute('x', 0);
// 		rect.setAttribute('y', 0);
// 		rect.setAttribute('width', this._size.x);
// 		rect.setAttribute('height', this._size.y);
// 		rect.setAttribute('fill', 'transparent');
// 		rect.setAttribute('stroke', 'black');
// 		rect.setAttribute('stroke-width', 2);
// 		this._rootGroup.appendChild(rect);
	},

	/// TODO: Modify _initPath to include an extra parameter, a group name
	/// to order symbolizers by z-index

	_addPath: function (layer) {
		this._rootGroup.appendChild(layer._path);
	},

});


L.svg.tile = function(tileSize, opts){
	return new L.SVG.Tile(tileSize, opts);
}




L.Canvas.Tile = L.Canvas.extend({

	initialize: function (tileSize, options) {
		L.Canvas.prototype.initialize.call(this, options);
		this._size = tileSize;

		this._initContainer();
		this._container.setAttribute('width', this._size.x);
		this._container.setAttribute('height', this._size.y);
		this._layers = {};
		this._drawnLayers = {};
	},

	getContainer: function() {
		return this._container;
	},

	onAdd: L.Util.FalseFn,

	_initContainer: function () {
		var container = this._container = document.createElement('canvas');

// 		L.DomEvent
// 			.on(container, 'mousemove', L.Util.throttle(this._onMouseMove, 32, this), this)
// 			.on(container, 'click dblclick mousedown mouseup contextmenu', this._onClick, this)
// 			.on(container, 'mouseout', this._handleMouseOut, this);

		this._ctx = container.getContext('2d');
	},


	/// TODO: Modify _initPath to include an extra parameter, a group name
	/// to order symbolizers by z-index

});


L.canvas.tile = function(tileSize, opts){
	return new L.Canvas.Tile(tileSize, opts);
}




L.VectorGrid = L.GridLayer.extend({

	options: {
		rendererFactory: L.svg.tile,
		vectorTileLayerStyles: {}
	},

	createTile: function(coords, done) {
		var renderer = this.options.rendererFactory(this.getTileSize(), this.options);

		var vectorTilePromise = this._getVectorTilePromise(coords);


		vectorTilePromise.then( function renderTile(vectorTile) {
			var this$1 = this;


			for (var layerName in vectorTile.layers) {
				var layer = vectorTile.layers[layerName];

				/// NOTE: THIS ASSUMES SQUARE TILES!!!!!1!
				var pxPerExtent = this$1.getTileSize().x / layer.extent;

				var layerStyle = this$1.options.vectorTileLayerStyles[ layerName ] ||
				L.Path.prototype.options;

				for (var i in layer.features) {
					var feat = layer.features[i];

					if (feat.type > 1) { // Lines, polygons

						this$1._mkFeatureParts(feat, pxPerExtent);

						/// Style can be a callback that is passed the feature's
						/// properties and tile zoom level...
						var styleOptions = (layerStyle instanceof Function) ?
						layerStyle(feat.properties, coords.z) :
						layerStyle;

						if (!(styleOptions instanceof Array)) {
							styleOptions = [styleOptions];
						}

						/// Style can be an array of styles, for styling a feature
						/// more than once...
						for (var j in styleOptions) {
							var style = L.extend({}, L.Path.prototype.options, styleOptions[j]);

							if (feat.type === 1) { // Points
								style.fill = false;
							} else if (feat.type === 2) {	// Polyline
								style.fill = false;
							}

							feat.options = style;
							renderer._initPath( feat );
							renderer._updateStyle( feat );

							if (feat.type === 1) { // Points
								// 							style.fill = false;
							} else if (feat.type === 2) {	// Polyline
								style.fill = false;
								renderer._updatePoly(feat, false);
							} else if (feat.type === 3) {	// Polygon
								renderer._updatePoly(feat, true);
							}

							renderer._addPath( feat );
						}

					} else {
						// Feat is a point (type === 1)

						/// FIXME!!!
					}
				}

			}
			L.Util.requestAnimFrame(done.bind(coords, null, null));
		}.bind(this));

		return renderer.getContainer();
	},



	// Fills up feat._parts based on the geometry and pxPerExtent,
	// pretty much as L.Polyline._projectLatLngs and L.Polyline._clipPoints
	// would do but simplified as the vectors are already simplified/clipped.
	_mkFeatureParts: function(feat, pxPerExtent) {

		var rings = feat.geometry;

		feat._parts = [];
		for (var i in rings) {
			var ring = rings[i];
			var part = [];
			for (var j in ring) {
				var coord = ring[j];
				if ('x' in coord) {
					// Protobuf vector tiles return {x: , y:}
					part.push(L.point(coord.x * pxPerExtent, coord.y * pxPerExtent));
				} else {
					// Geojson-vt returns [,]
					part.push(L.point(coord[0] * pxPerExtent, coord[1] * pxPerExtent));
				}
			}
			feat._parts.push(part);
		}

	},

});



L.vectorGrid = function (options) {
	return new L.VectorGrid(options);
};




L.VectorGrid.Slicer = L.VectorGrid.extend({

	options: {
		vectorTileLayerName: 'sliced',
		extent: 4096,	// Default for geojson-vt
		maxZoom: 14  	// Default for geojson-vt
	},

	initialize: function(geojson, options) {
		var this$1 = this;

		L.VectorGrid.prototype.initialize.call(this, options);

		// Slice the geojson/topojson via a web worker
		var workerCode = "\n\t\t\t(function(f){if(typeof exports===\"object\"&&typeof module!==\"undefined\"){module.exports=f()}else if(typeof define===\"function\"&&define.amd){define([],f)}else{var g;if(typeof window!==\"undefined\"){g=window}else if(typeof global!==\"undefined\"){g=global}else if(typeof self!==\"undefined\"){g=self}else{g=this}g.geojsonvt = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require==\"function\"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error(\"Cannot find module '\"+o+\"'\");throw f.code=\"MODULE_NOT_FOUND\",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require==\"function\"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){\n'use strict';\n\nmodule.exports = clip;\n\n/* clip features between two axis-parallel lines:\n *     |        |\n *  ___|___     |     /\n * /   |   ____|____/\n *     |        |\n */\n\nfunction clip(features, scale, k1, k2, axis, intersect, minAll, maxAll) {\n\n    k1 /= scale;\n    k2 /= scale;\n\n    if (minAll >= k1 && maxAll <= k2) return features; // trivial accept\n    else if (minAll > k2 || maxAll < k1) return null; // trivial reject\n\n    var clipped = [];\n\n    for (var i = 0; i < features.length; i++) {\n\n        var feature = features[i],\n            geometry = feature.geometry,\n            type = feature.type,\n            min, max;\n\n        min = feature.min[axis];\n        max = feature.max[axis];\n\n        if (min >= k1 && max <= k2) { // trivial accept\n            clipped.push(feature);\n            continue;\n        } else if (min > k2 || max < k1) continue; // trivial reject\n\n        var slices = type === 1 ?\n                clipPoints(geometry, k1, k2, axis) :\n                clipGeometry(geometry, k1, k2, axis, intersect, type === 3);\n\n        if (slices.length) {\n            // if a feature got clipped, it will likely get clipped on the next zoom level as well,\n            // so there's no need to recalculate bboxes\n            clipped.push({\n                geometry: slices,\n                type: type,\n                tags: features[i].tags || null,\n                min: feature.min,\n                max: feature.max\n            });\n        }\n    }\n\n    return clipped.length ? clipped : null;\n}\n\nfunction clipPoints(geometry, k1, k2, axis) {\n    var slice = [];\n\n    for (var i = 0; i < geometry.length; i++) {\n        var a = geometry[i],\n            ak = a[axis];\n\n        if (ak >= k1 && ak <= k2) slice.push(a);\n    }\n    return slice;\n}\n\nfunction clipGeometry(geometry, k1, k2, axis, intersect, closed) {\n\n    var slices = [];\n\n    for (var i = 0; i < geometry.length; i++) {\n\n        var ak = 0,\n            bk = 0,\n            b = null,\n            points = geometry[i],\n            area = points.area,\n            dist = points.dist,\n            len = points.length,\n            a, j, last;\n\n        var slice = [];\n\n        for (j = 0; j < len - 1; j++) {\n            a = b || points[j];\n            b = points[j + 1];\n            ak = bk || a[axis];\n            bk = b[axis];\n\n            if (ak < k1) {\n\n                if ((bk > k2)) { // ---|-----|-->\n                    slice.push(intersect(a, b, k1), intersect(a, b, k2));\n                    if (!closed) slice = newSlice(slices, slice, area, dist);\n\n                } else if (bk >= k1) slice.push(intersect(a, b, k1)); // ---|-->  |\n\n            } else if (ak > k2) {\n\n                if ((bk < k1)) { // <--|-----|---\n                    slice.push(intersect(a, b, k2), intersect(a, b, k1));\n                    if (!closed) slice = newSlice(slices, slice, area, dist);\n\n                } else if (bk <= k2) slice.push(intersect(a, b, k2)); // |  <--|---\n\n            } else {\n\n                slice.push(a);\n\n                if (bk < k1) { // <--|---  |\n                    slice.push(intersect(a, b, k1));\n                    if (!closed) slice = newSlice(slices, slice, area, dist);\n\n                } else if (bk > k2) { // |  ---|-->\n                    slice.push(intersect(a, b, k2));\n                    if (!closed) slice = newSlice(slices, slice, area, dist);\n                }\n                // | --> |\n            }\n        }\n\n        // add the last point\n        a = points[len - 1];\n        ak = a[axis];\n        if (ak >= k1 && ak <= k2) slice.push(a);\n\n        // close the polygon if its endpoints are not the same after clipping\n\n        last = slice[slice.length - 1];\n        if (closed && last && (slice[0][0] !== last[0] || slice[0][1] !== last[1])) slice.push(slice[0]);\n\n        // add the final slice\n        newSlice(slices, slice, area, dist);\n    }\n\n    return slices;\n}\n\nfunction newSlice(slices, slice, area, dist) {\n    if (slice.length) {\n        // we don't recalculate the area/length of the unclipped geometry because the case where it goes\n        // below the visibility threshold as a result of clipping is rare, so we avoid doing unnecessary work\n        slice.area = area;\n        slice.dist = dist;\n\n        slices.push(slice);\n    }\n    return [];\n}\n\n},{}],2:[function(require,module,exports){\n'use strict';\n\nmodule.exports = convert;\n\nvar simplify = require('./simplify');\n\n// converts GeoJSON feature into an intermediate projected JSON vector format with simplification data\n\nfunction convert(data, tolerance) {\n    var features = [];\n\n    if (data.type === 'FeatureCollection') {\n        for (var i = 0; i < data.features.length; i++) {\n            convertFeature(features, data.features[i], tolerance);\n        }\n    } else if (data.type === 'Feature') {\n        convertFeature(features, data, tolerance);\n\n    } else {\n        // single geometry or a geometry collection\n        convertFeature(features, {geometry: data}, tolerance);\n    }\n    return features;\n}\n\nfunction convertFeature(features, feature, tolerance) {\n    var geom = feature.geometry,\n        type = geom.type,\n        coords = geom.coordinates,\n        tags = feature.properties,\n        i, j, rings;\n\n    if (type === 'Point') {\n        features.push(create(tags, 1, [projectPoint(coords)]));\n\n    } else if (type === 'MultiPoint') {\n        features.push(create(tags, 1, project(coords)));\n\n    } else if (type === 'LineString') {\n        features.push(create(tags, 2, [project(coords, tolerance)]));\n\n    } else if (type === 'MultiLineString' || type === 'Polygon') {\n        rings = [];\n        for (i = 0; i < coords.length; i++) {\n            rings.push(project(coords[i], tolerance));\n        }\n        features.push(create(tags, type === 'Polygon' ? 3 : 2, rings));\n\n    } else if (type === 'MultiPolygon') {\n        rings = [];\n        for (i = 0; i < coords.length; i++) {\n            for (j = 0; j < coords[i].length; j++) {\n                rings.push(project(coords[i][j], tolerance));\n            }\n        }\n        features.push(create(tags, 3, rings));\n\n    } else if (type === 'GeometryCollection') {\n        for (i = 0; i < geom.geometries.length; i++) {\n            convertFeature(features, {\n                geometry: geom.geometries[i],\n                properties: tags\n            }, tolerance);\n        }\n\n    } else {\n        throw new Error('Input data is not a valid GeoJSON object.');\n    }\n}\n\nfunction create(tags, type, geometry) {\n    var feature = {\n        geometry: geometry,\n        type: type,\n        tags: tags || null,\n        min: [2, 1], // initial bbox values;\n        max: [-1, 0]  // note that coords are usually in [0..1] range\n    };\n    calcBBox(feature);\n    return feature;\n}\n\nfunction project(lonlats, tolerance) {\n    var projected = [];\n    for (var i = 0; i < lonlats.length; i++) {\n        projected.push(projectPoint(lonlats[i]));\n    }\n    if (tolerance) {\n        simplify(projected, tolerance);\n        calcSize(projected);\n    }\n    return projected;\n}\n\nfunction projectPoint(p) {\n    var sin = Math.sin(p[1] * Math.PI / 180),\n        x = (p[0] / 360 + 0.5),\n        y = (0.5 - 0.25 * Math.log((1 + sin) / (1 - sin)) / Math.PI);\n\n    y = y < -1 ? -1 :\n        y > 1 ? 1 : y;\n\n    return [x, y, 0];\n}\n\n// calculate area and length of the poly\nfunction calcSize(points) {\n    var area = 0,\n        dist = 0;\n\n    for (var i = 0, a, b; i < points.length - 1; i++) {\n        a = b || points[i];\n        b = points[i + 1];\n\n        area += a[0] * b[1] - b[0] * a[1];\n\n        // use Manhattan distance instead of Euclidian one to avoid expensive square root computation\n        dist += Math.abs(b[0] - a[0]) + Math.abs(b[1] - a[1]);\n    }\n    points.area = Math.abs(area / 2);\n    points.dist = dist;\n}\n\n// calculate the feature bounding box for faster clipping later\nfunction calcBBox(feature) {\n    var geometry = feature.geometry,\n        min = feature.min,\n        max = feature.max;\n\n    if (feature.type === 1) calcRingBBox(min, max, geometry);\n    else for (var i = 0; i < geometry.length; i++) calcRingBBox(min, max, geometry[i]);\n\n    return feature;\n}\n\nfunction calcRingBBox(min, max, points) {\n    for (var i = 0, p; i < points.length; i++) {\n        p = points[i];\n        min[0] = Math.min(p[0], min[0]);\n        max[0] = Math.max(p[0], max[0]);\n        min[1] = Math.min(p[1], min[1]);\n        max[1] = Math.max(p[1], max[1]);\n    }\n}\n\n},{\"./simplify\":4}],3:[function(require,module,exports){\n'use strict';\n\nmodule.exports = geojsonvt;\n\nvar convert = require('./convert'),     // GeoJSON conversion and preprocessing\n    transform = require('./transform'), // coordinate transformation\n    clip = require('./clip'),           // stripe clipping algorithm\n    wrap = require('./wrap'),           // date line processing\n    createTile = require('./tile');     // final simplified tile generation\n\n\nfunction geojsonvt(data, options) {\n    return new GeoJSONVT(data, options);\n}\n\nfunction GeoJSONVT(data, options) {\n    options = this.options = extend(Object.create(this.options), options);\n\n    var debug = options.debug;\n\n    if (debug) console.time('preprocess data');\n\n    var z2 = 1 << options.maxZoom, // 2^z\n        features = convert(data, options.tolerance / (z2 * options.extent));\n\n    this.tiles = {};\n    this.tileCoords = [];\n\n    if (debug) {\n        console.timeEnd('preprocess data');\n        console.log('index: maxZoom: %d, maxPoints: %d', options.indexMaxZoom, options.indexMaxPoints);\n        console.time('generate tiles');\n        this.stats = {};\n        this.total = 0;\n    }\n\n    features = wrap(features, options.buffer / options.extent, intersectX);\n\n    // start slicing from the top tile down\n    if (features.length) this.splitTile(features, 0, 0, 0);\n\n    if (debug) {\n        if (features.length) console.log('features: %d, points: %d', this.tiles[0].numFeatures, this.tiles[0].numPoints);\n        console.timeEnd('generate tiles');\n        console.log('tiles generated:', this.total, JSON.stringify(this.stats));\n    }\n}\n\nGeoJSONVT.prototype.options = {\n    maxZoom: 14,            // max zoom to preserve detail on\n    indexMaxZoom: 5,        // max zoom in the tile index\n    indexMaxPoints: 100000, // max number of points per tile in the tile index\n    solidChildren: false,   // whether to tile solid square tiles further\n    tolerance: 3,           // simplification tolerance (higher means simpler)\n    extent: 4096,           // tile extent\n    buffer: 64,             // tile buffer on each side\n    debug: 0                // logging level (0, 1 or 2)\n};\n\nGeoJSONVT.prototype.splitTile = function (features, z, x, y, cz, cx, cy) {\n\n    var stack = [features, z, x, y],\n        options = this.options,\n        debug = options.debug,\n        solid = null;\n\n    // avoid recursion by using a processing queue\n    while (stack.length) {\n        y = stack.pop();\n        x = stack.pop();\n        z = stack.pop();\n        features = stack.pop();\n\n        var z2 = 1 << z,\n            id = toID(z, x, y),\n            tile = this.tiles[id],\n            tileTolerance = z === options.maxZoom ? 0 : options.tolerance / (z2 * options.extent);\n\n        if (!tile) {\n            if (debug > 1) console.time('creation');\n\n            tile = this.tiles[id] = createTile(features, z2, x, y, tileTolerance, z === options.maxZoom);\n            this.tileCoords.push({z: z, x: x, y: y});\n\n            if (debug) {\n                if (debug > 1) {\n                    console.log('tile z%d-%d-%d (features: %d, points: %d, simplified: %d)',\n                        z, x, y, tile.numFeatures, tile.numPoints, tile.numSimplified);\n                    console.timeEnd('creation');\n                }\n                var key = 'z' + z;\n                this.stats[key] = (this.stats[key] || 0) + 1;\n                this.total++;\n            }\n        }\n\n        // save reference to original geometry in tile so that we can drill down later if we stop now\n        tile.source = features;\n\n        // if it's the first-pass tiling\n        if (!cz) {\n            // stop tiling if we reached max zoom, or if the tile is too simple\n            if (z === options.indexMaxZoom || tile.numPoints <= options.indexMaxPoints) continue;\n\n        // if a drilldown to a specific tile\n        } else {\n            // stop tiling if we reached base zoom or our target tile zoom\n            if (z === options.maxZoom || z === cz) continue;\n\n            // stop tiling if it's not an ancestor of the target tile\n            var m = 1 << (cz - z);\n            if (x !== Math.floor(cx / m) || y !== Math.floor(cy / m)) continue;\n        }\n\n        // stop tiling if the tile is solid clipped square\n        if (!options.solidChildren && isClippedSquare(tile, options.extent, options.buffer)) {\n            if (cz) solid = z; // and remember the zoom if we're drilling down\n            continue;\n        }\n\n        // if we slice further down, no need to keep source geometry\n        tile.source = null;\n\n        if (debug > 1) console.time('clipping');\n\n        // values we'll use for clipping\n        var k1 = 0.5 * options.buffer / options.extent,\n            k2 = 0.5 - k1,\n            k3 = 0.5 + k1,\n            k4 = 1 + k1,\n            tl, bl, tr, br, left, right;\n\n        tl = bl = tr = br = null;\n\n        left  = clip(features, z2, x - k1, x + k3, 0, intersectX, tile.min[0], tile.max[0]);\n        right = clip(features, z2, x + k2, x + k4, 0, intersectX, tile.min[0], tile.max[0]);\n\n        if (left) {\n            tl = clip(left, z2, y - k1, y + k3, 1, intersectY, tile.min[1], tile.max[1]);\n            bl = clip(left, z2, y + k2, y + k4, 1, intersectY, tile.min[1], tile.max[1]);\n        }\n\n        if (right) {\n            tr = clip(right, z2, y - k1, y + k3, 1, intersectY, tile.min[1], tile.max[1]);\n            br = clip(right, z2, y + k2, y + k4, 1, intersectY, tile.min[1], tile.max[1]);\n        }\n\n        if (debug > 1) console.timeEnd('clipping');\n\n        if (tl) stack.push(tl, z + 1, x * 2,     y * 2);\n        if (bl) stack.push(bl, z + 1, x * 2,     y * 2 + 1);\n        if (tr) stack.push(tr, z + 1, x * 2 + 1, y * 2);\n        if (br) stack.push(br, z + 1, x * 2 + 1, y * 2 + 1);\n    }\n\n    return solid;\n};\n\nGeoJSONVT.prototype.getTile = function (z, x, y) {\n    var options = this.options,\n        extent = options.extent,\n        debug = options.debug;\n\n    var z2 = 1 << z;\n    x = ((x % z2) + z2) % z2; // wrap tile x coordinate\n\n    var id = toID(z, x, y);\n    if (this.tiles[id]) return transform.tile(this.tiles[id], extent);\n\n    if (debug > 1) console.log('drilling down to z%d-%d-%d', z, x, y);\n\n    var z0 = z,\n        x0 = x,\n        y0 = y,\n        parent;\n\n    while (!parent && z0 > 0) {\n        z0--;\n        x0 = Math.floor(x0 / 2);\n        y0 = Math.floor(y0 / 2);\n        parent = this.tiles[toID(z0, x0, y0)];\n    }\n\n    if (!parent || !parent.source) return null;\n\n    // if we found a parent tile containing the original geometry, we can drill down from it\n    if (debug > 1) console.log('found parent tile z%d-%d-%d', z0, x0, y0);\n\n    // it parent tile is a solid clipped square, return it instead since it's identical\n    if (isClippedSquare(parent, extent, options.buffer)) return transform.tile(parent, extent);\n\n    if (debug > 1) console.time('drilling down');\n    var solid = this.splitTile(parent.source, z0, x0, y0, z, x, y);\n    if (debug > 1) console.timeEnd('drilling down');\n\n    // one of the parent tiles was a solid clipped square\n    if (solid !== null) {\n        var m = 1 << (z - solid);\n        id = toID(solid, Math.floor(x / m), Math.floor(y / m));\n    }\n\n    return this.tiles[id] ? transform.tile(this.tiles[id], extent) : null;\n};\n\nfunction toID(z, x, y) {\n    return (((1 << z) * y + x) * 32) + z;\n}\n\nfunction intersectX(a, b, x) {\n    return [x, (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0]) + a[1], 1];\n}\nfunction intersectY(a, b, y) {\n    return [(y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]) + a[0], y, 1];\n}\n\nfunction extend(dest, src) {\n    for (var i in src) dest[i] = src[i];\n    return dest;\n}\n\n// checks whether a tile is a whole-area fill after clipping; if it is, there's no sense slicing it further\nfunction isClippedSquare(tile, extent, buffer) {\n\n    var features = tile.source;\n    if (features.length !== 1) return false;\n\n    var feature = features[0];\n    if (feature.type !== 3 || feature.geometry.length > 1) return false;\n\n    var len = feature.geometry[0].length;\n    if (len !== 5) return false;\n\n    for (var i = 0; i < len; i++) {\n        var p = transform.point(feature.geometry[0][i], extent, tile.z2, tile.x, tile.y);\n        if ((p[0] !== -buffer && p[0] !== extent + buffer) ||\n            (p[1] !== -buffer && p[1] !== extent + buffer)) return false;\n    }\n\n    return true;\n}\n\n},{\"./clip\":1,\"./convert\":2,\"./tile\":5,\"./transform\":6,\"./wrap\":7}],4:[function(require,module,exports){\n'use strict';\n\nmodule.exports = simplify;\n\n// calculate simplification data using optimized Douglas-Peucker algorithm\n\nfunction simplify(points, tolerance) {\n\n    var sqTolerance = tolerance * tolerance,\n        len = points.length,\n        first = 0,\n        last = len - 1,\n        stack = [],\n        i, maxSqDist, sqDist, index;\n\n    // always retain the endpoints (1 is the max value)\n    points[first][2] = 1;\n    points[last][2] = 1;\n\n    // avoid recursion by using a stack\n    while (last) {\n\n        maxSqDist = 0;\n\n        for (i = first + 1; i < last; i++) {\n            sqDist = getSqSegDist(points[i], points[first], points[last]);\n\n            if (sqDist > maxSqDist) {\n                index = i;\n                maxSqDist = sqDist;\n            }\n        }\n\n        if (maxSqDist > sqTolerance) {\n            points[index][2] = maxSqDist; // save the point importance in squared pixels as a z coordinate\n            stack.push(first);\n            stack.push(index);\n            first = index;\n\n        } else {\n            last = stack.pop();\n            first = stack.pop();\n        }\n    }\n}\n\n// square distance from a point to a segment\nfunction getSqSegDist(p, a, b) {\n\n    var x = a[0], y = a[1],\n        bx = b[0], by = b[1],\n        px = p[0], py = p[1],\n        dx = bx - x,\n        dy = by - y;\n\n    if (dx !== 0 || dy !== 0) {\n\n        var t = ((px - x) * dx + (py - y) * dy) / (dx * dx + dy * dy);\n\n        if (t > 1) {\n            x = bx;\n            y = by;\n\n        } else if (t > 0) {\n            x += dx * t;\n            y += dy * t;\n        }\n    }\n\n    dx = px - x;\n    dy = py - y;\n\n    return dx * dx + dy * dy;\n}\n\n},{}],5:[function(require,module,exports){\n'use strict';\n\nmodule.exports = createTile;\n\nfunction createTile(features, z2, tx, ty, tolerance, noSimplify) {\n    var tile = {\n        features: [],\n        numPoints: 0,\n        numSimplified: 0,\n        numFeatures: 0,\n        source: null,\n        x: tx,\n        y: ty,\n        z2: z2,\n        transformed: false,\n        min: [2, 1],\n        max: [-1, 0]\n    };\n    for (var i = 0; i < features.length; i++) {\n        tile.numFeatures++;\n        addFeature(tile, features[i], tolerance, noSimplify);\n\n        var min = features[i].min,\n            max = features[i].max;\n\n        if (min[0] < tile.min[0]) tile.min[0] = min[0];\n        if (min[1] < tile.min[1]) tile.min[1] = min[1];\n        if (max[0] > tile.max[0]) tile.max[0] = max[0];\n        if (max[1] > tile.max[1]) tile.max[1] = max[1];\n    }\n    return tile;\n}\n\nfunction addFeature(tile, feature, tolerance, noSimplify) {\n\n    var geom = feature.geometry,\n        type = feature.type,\n        simplified = [],\n        sqTolerance = tolerance * tolerance,\n        i, j, ring, p;\n\n    if (type === 1) {\n        for (i = 0; i < geom.length; i++) {\n            simplified.push(geom[i]);\n            tile.numPoints++;\n            tile.numSimplified++;\n        }\n\n    } else {\n\n        // simplify and transform projected coordinates for tile geometry\n        for (i = 0; i < geom.length; i++) {\n            ring = geom[i];\n\n            // filter out tiny polylines & polygons\n            if (!noSimplify && ((type === 2 && ring.dist < tolerance) ||\n                                (type === 3 && ring.area < sqTolerance))) {\n                tile.numPoints += ring.length;\n                continue;\n            }\n\n            var simplifiedRing = [];\n\n            for (j = 0; j < ring.length; j++) {\n                p = ring[j];\n                // keep points with importance > tolerance\n                if (noSimplify || p[2] > sqTolerance) {\n                    simplifiedRing.push(p);\n                    tile.numSimplified++;\n                }\n                tile.numPoints++;\n            }\n\n            simplified.push(simplifiedRing);\n        }\n    }\n\n    if (simplified.length) {\n        tile.features.push({\n            geometry: simplified,\n            type: type,\n            tags: feature.tags || null\n        });\n    }\n}\n\n},{}],6:[function(require,module,exports){\n'use strict';\n\nexports.tile = transformTile;\nexports.point = transformPoint;\n\n// Transforms the coordinates of each feature in the given tile from\n// mercator-projected space into (extent x extent) tile space.\nfunction transformTile(tile, extent) {\n    if (tile.transformed) return tile;\n\n    var z2 = tile.z2,\n        tx = tile.x,\n        ty = tile.y,\n        i, j, k;\n\n    for (i = 0; i < tile.features.length; i++) {\n        var feature = tile.features[i],\n            geom = feature.geometry,\n            type = feature.type;\n\n        if (type === 1) {\n            for (j = 0; j < geom.length; j++) geom[j] = transformPoint(geom[j], extent, z2, tx, ty);\n\n        } else {\n            for (j = 0; j < geom.length; j++) {\n                var ring = geom[j];\n                for (k = 0; k < ring.length; k++) ring[k] = transformPoint(ring[k], extent, z2, tx, ty);\n            }\n        }\n    }\n\n    tile.transformed = true;\n\n    return tile;\n}\n\nfunction transformPoint(p, extent, z2, tx, ty) {\n    var x = Math.round(extent * (p[0] * z2 - tx)),\n        y = Math.round(extent * (p[1] * z2 - ty));\n    return [x, y];\n}\n\n},{}],7:[function(require,module,exports){\n'use strict';\n\nvar clip = require('./clip');\n\nmodule.exports = wrap;\n\nfunction wrap(features, buffer, intersectX) {\n    var merged = features,\n        left  = clip(features, 1, -1 - buffer, buffer,     0, intersectX, -1, 2), // left world copy\n        right = clip(features, 1,  1 - buffer, 2 + buffer, 0, intersectX, -1, 2); // right world copy\n\n    if (left || right) {\n        merged = clip(features, 1, -buffer, 1 + buffer, 0, intersectX, -1, 2); // center world copy\n\n        if (left) merged = shiftFeatureCoords(left, 1).concat(merged); // merge left into center\n        if (right) merged = merged.concat(shiftFeatureCoords(right, -1)); // merge right into center\n    }\n\n    return merged;\n}\n\nfunction shiftFeatureCoords(features, offset) {\n    var newFeatures = [];\n\n    for (var i = 0; i < features.length; i++) {\n        var feature = features[i],\n            type = feature.type;\n\n        var newGeometry;\n\n        if (type === 1) {\n            newGeometry = shiftCoords(feature.geometry, offset);\n        } else {\n            newGeometry = [];\n            for (var j = 0; j < feature.geometry.length; j++) {\n                newGeometry.push(shiftCoords(feature.geometry[j], offset));\n            }\n        }\n\n        newFeatures.push({\n            geometry: newGeometry,\n            type: type,\n            tags: feature.tags,\n            min: [feature.min[0] + offset, feature.min[1]],\n            max: [feature.max[0] + offset, feature.max[1]]\n        });\n    }\n\n    return newFeatures;\n}\n\nfunction shiftCoords(points, offset) {\n    var newPoints = [];\n    newPoints.area = points.area;\n    newPoints.dist = points.dist;\n\n    for (var i = 0; i < points.length; i++) {\n        newPoints.push([points[i][0] + offset, points[i][1], points[i][2]]);\n    }\n    return newPoints;\n}\n\n},{\"./clip\":1}]},{},[3])(3)\n});\n\n\t\t\t(function (global, factory) {\n  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :\n  typeof define === 'function' && define.amd ? define(['exports'], factory) :\n  (factory((global.topojson = global.topojson || {})));\n}(this, function (exports) { 'use strict';\n\n  function noop() {}\n\n  function transformAbsolute(transform) {\n    if (!transform) return noop;\n    var x0,\n        y0,\n        kx = transform.scale[0],\n        ky = transform.scale[1],\n        dx = transform.translate[0],\n        dy = transform.translate[1];\n    return function(point, i) {\n      if (!i) x0 = y0 = 0;\n      point[0] = (x0 += point[0]) * kx + dx;\n      point[1] = (y0 += point[1]) * ky + dy;\n    };\n  }\n\n  function transformRelative(transform) {\n    if (!transform) return noop;\n    var x0,\n        y0,\n        kx = transform.scale[0],\n        ky = transform.scale[1],\n        dx = transform.translate[0],\n        dy = transform.translate[1];\n    return function(point, i) {\n      if (!i) x0 = y0 = 0;\n      var x1 = Math.round((point[0] - dx) / kx),\n          y1 = Math.round((point[1] - dy) / ky);\n      point[0] = x1 - x0;\n      point[1] = y1 - y0;\n      x0 = x1;\n      y0 = y1;\n    };\n  }\n\n  function reverse(array, n) {\n    var t, j = array.length, i = j - n;\n    while (i < --j) t = array[i], array[i++] = array[j], array[j] = t;\n  }\n\n  function bisect(a, x) {\n    var lo = 0, hi = a.length;\n    while (lo < hi) {\n      var mid = lo + hi >>> 1;\n      if (a[mid] < x) lo = mid + 1;\n      else hi = mid;\n    }\n    return lo;\n  }\n\n  function feature(topology, o) {\n    return o.type === \"GeometryCollection\" ? {\n      type: \"FeatureCollection\",\n      features: o.geometries.map(function(o) { return feature$1(topology, o); })\n    } : feature$1(topology, o);\n  }\n\n  function feature$1(topology, o) {\n    var f = {\n      type: \"Feature\",\n      id: o.id,\n      properties: o.properties || {},\n      geometry: object(topology, o)\n    };\n    if (o.id == null) delete f.id;\n    return f;\n  }\n\n  function object(topology, o) {\n    var absolute = transformAbsolute(topology.transform),\n        arcs = topology.arcs;\n\n    function arc(i, points) {\n      if (points.length) points.pop();\n      for (var a = arcs[i < 0 ? ~i : i], k = 0, n = a.length, p; k < n; ++k) {\n        points.push(p = a[k].slice());\n        absolute(p, k);\n      }\n      if (i < 0) reverse(points, n);\n    }\n\n    function point(p) {\n      p = p.slice();\n      absolute(p, 0);\n      return p;\n    }\n\n    function line(arcs) {\n      var points = [];\n      for (var i = 0, n = arcs.length; i < n; ++i) arc(arcs[i], points);\n      if (points.length < 2) points.push(points[0].slice());\n      return points;\n    }\n\n    function ring(arcs) {\n      var points = line(arcs);\n      while (points.length < 4) points.push(points[0].slice());\n      return points;\n    }\n\n    function polygon(arcs) {\n      return arcs.map(ring);\n    }\n\n    function geometry(o) {\n      var t = o.type;\n      return t === \"GeometryCollection\" ? {type: t, geometries: o.geometries.map(geometry)}\n          : t in geometryType ? {type: t, coordinates: geometryType[t](o)}\n          : null;\n    }\n\n    var geometryType = {\n      Point: function(o) { return point(o.coordinates); },\n      MultiPoint: function(o) { return o.coordinates.map(point); },\n      LineString: function(o) { return line(o.arcs); },\n      MultiLineString: function(o) { return o.arcs.map(line); },\n      Polygon: function(o) { return polygon(o.arcs); },\n      MultiPolygon: function(o) { return o.arcs.map(polygon); }\n    };\n\n    return geometry(o);\n  }\n\n  function stitchArcs(topology, arcs) {\n    var stitchedArcs = {},\n        fragmentByStart = {},\n        fragmentByEnd = {},\n        fragments = [],\n        emptyIndex = -1;\n\n    // Stitch empty arcs first, since they may be subsumed by other arcs.\n    arcs.forEach(function(i, j) {\n      var arc = topology.arcs[i < 0 ? ~i : i], t;\n      if (arc.length < 3 && !arc[1][0] && !arc[1][1]) {\n        t = arcs[++emptyIndex], arcs[emptyIndex] = i, arcs[j] = t;\n      }\n    });\n\n    arcs.forEach(function(i) {\n      var e = ends(i),\n          start = e[0],\n          end = e[1],\n          f, g;\n\n      if (f = fragmentByEnd[start]) {\n        delete fragmentByEnd[f.end];\n        f.push(i);\n        f.end = end;\n        if (g = fragmentByStart[end]) {\n          delete fragmentByStart[g.start];\n          var fg = g === f ? f : f.concat(g);\n          fragmentByStart[fg.start = f.start] = fragmentByEnd[fg.end = g.end] = fg;\n        } else {\n          fragmentByStart[f.start] = fragmentByEnd[f.end] = f;\n        }\n      } else if (f = fragmentByStart[end]) {\n        delete fragmentByStart[f.start];\n        f.unshift(i);\n        f.start = start;\n        if (g = fragmentByEnd[start]) {\n          delete fragmentByEnd[g.end];\n          var gf = g === f ? f : g.concat(f);\n          fragmentByStart[gf.start = g.start] = fragmentByEnd[gf.end = f.end] = gf;\n        } else {\n          fragmentByStart[f.start] = fragmentByEnd[f.end] = f;\n        }\n      } else {\n        f = [i];\n        fragmentByStart[f.start = start] = fragmentByEnd[f.end = end] = f;\n      }\n    });\n\n    function ends(i) {\n      var arc = topology.arcs[i < 0 ? ~i : i], p0 = arc[0], p1;\n      if (topology.transform) p1 = [0, 0], arc.forEach(function(dp) { p1[0] += dp[0], p1[1] += dp[1]; });\n      else p1 = arc[arc.length - 1];\n      return i < 0 ? [p1, p0] : [p0, p1];\n    }\n\n    function flush(fragmentByEnd, fragmentByStart) {\n      for (var k in fragmentByEnd) {\n        var f = fragmentByEnd[k];\n        delete fragmentByStart[f.start];\n        delete f.start;\n        delete f.end;\n        f.forEach(function(i) { stitchedArcs[i < 0 ? ~i : i] = 1; });\n        fragments.push(f);\n      }\n    }\n\n    flush(fragmentByEnd, fragmentByStart);\n    flush(fragmentByStart, fragmentByEnd);\n    arcs.forEach(function(i) { if (!stitchedArcs[i < 0 ? ~i : i]) fragments.push([i]); });\n\n    return fragments;\n  }\n\n  function mesh(topology) {\n    return object(topology, meshArcs.apply(this, arguments));\n  }\n\n  function meshArcs(topology, o, filter) {\n    var arcs = [];\n\n    function arc(i) {\n      var j = i < 0 ? ~i : i;\n      (geomsByArc[j] || (geomsByArc[j] = [])).push({i: i, g: geom});\n    }\n\n    function line(arcs) {\n      arcs.forEach(arc);\n    }\n\n    function polygon(arcs) {\n      arcs.forEach(line);\n    }\n\n    function geometry(o) {\n      if (o.type === \"GeometryCollection\") o.geometries.forEach(geometry);\n      else if (o.type in geometryType) geom = o, geometryType[o.type](o.arcs);\n    }\n\n    if (arguments.length > 1) {\n      var geomsByArc = [],\n          geom;\n\n      var geometryType = {\n        LineString: line,\n        MultiLineString: polygon,\n        Polygon: polygon,\n        MultiPolygon: function(arcs) { arcs.forEach(polygon); }\n      };\n\n      geometry(o);\n\n      geomsByArc.forEach(arguments.length < 3\n          ? function(geoms) { arcs.push(geoms[0].i); }\n          : function(geoms) { if (filter(geoms[0].g, geoms[geoms.length - 1].g)) arcs.push(geoms[0].i); });\n    } else {\n      for (var i = 0, n = topology.arcs.length; i < n; ++i) arcs.push(i);\n    }\n\n    return {type: \"MultiLineString\", arcs: stitchArcs(topology, arcs)};\n  }\n\n  function cartesianTriangleArea(triangle) {\n    var a = triangle[0], b = triangle[1], c = triangle[2];\n    return Math.abs((a[0] - c[0]) * (b[1] - a[1]) - (a[0] - b[0]) * (c[1] - a[1]));\n  }\n\n  function ring(ring) {\n    var i = -1,\n        n = ring.length,\n        a,\n        b = ring[n - 1],\n        area = 0;\n\n    while (++i < n) {\n      a = b;\n      b = ring[i];\n      area += a[0] * b[1] - a[1] * b[0];\n    }\n\n    return area / 2;\n  }\n\n  function merge(topology) {\n    return object(topology, mergeArcs.apply(this, arguments));\n  }\n\n  function mergeArcs(topology, objects) {\n    var polygonsByArc = {},\n        polygons = [],\n        components = [];\n\n    objects.forEach(function(o) {\n      if (o.type === \"Polygon\") register(o.arcs);\n      else if (o.type === \"MultiPolygon\") o.arcs.forEach(register);\n    });\n\n    function register(polygon) {\n      polygon.forEach(function(ring$$) {\n        ring$$.forEach(function(arc) {\n          (polygonsByArc[arc = arc < 0 ? ~arc : arc] || (polygonsByArc[arc] = [])).push(polygon);\n        });\n      });\n      polygons.push(polygon);\n    }\n\n    function area(ring$$) {\n      return Math.abs(ring(object(topology, {type: \"Polygon\", arcs: [ring$$]}).coordinates[0]));\n    }\n\n    polygons.forEach(function(polygon) {\n      if (!polygon._) {\n        var component = [],\n            neighbors = [polygon];\n        polygon._ = 1;\n        components.push(component);\n        while (polygon = neighbors.pop()) {\n          component.push(polygon);\n          polygon.forEach(function(ring$$) {\n            ring$$.forEach(function(arc) {\n              polygonsByArc[arc < 0 ? ~arc : arc].forEach(function(polygon) {\n                if (!polygon._) {\n                  polygon._ = 1;\n                  neighbors.push(polygon);\n                }\n              });\n            });\n          });\n        }\n      }\n    });\n\n    polygons.forEach(function(polygon) {\n      delete polygon._;\n    });\n\n    return {\n      type: \"MultiPolygon\",\n      arcs: components.map(function(polygons) {\n        var arcs = [], n;\n\n        // Extract the exterior (unique) arcs.\n        polygons.forEach(function(polygon) {\n          polygon.forEach(function(ring$$) {\n            ring$$.forEach(function(arc) {\n              if (polygonsByArc[arc < 0 ? ~arc : arc].length < 2) {\n                arcs.push(arc);\n              }\n            });\n          });\n        });\n\n        // Stitch the arcs into one or more rings.\n        arcs = stitchArcs(topology, arcs);\n\n        // If more than one ring is returned,\n        // at most one of these rings can be the exterior;\n        // choose the one with the greatest absolute area.\n        if ((n = arcs.length) > 1) {\n          for (var i = 1, k = area(arcs[0]), ki, t; i < n; ++i) {\n            if ((ki = area(arcs[i])) > k) {\n              t = arcs[0], arcs[0] = arcs[i], arcs[i] = t, k = ki;\n            }\n          }\n        }\n\n        return arcs;\n      })\n    };\n  }\n\n  function neighbors(objects) {\n    var indexesByArc = {}, // arc index -> array of object indexes\n        neighbors = objects.map(function() { return []; });\n\n    function line(arcs, i) {\n      arcs.forEach(function(a) {\n        if (a < 0) a = ~a;\n        var o = indexesByArc[a];\n        if (o) o.push(i);\n        else indexesByArc[a] = [i];\n      });\n    }\n\n    function polygon(arcs, i) {\n      arcs.forEach(function(arc) { line(arc, i); });\n    }\n\n    function geometry(o, i) {\n      if (o.type === \"GeometryCollection\") o.geometries.forEach(function(o) { geometry(o, i); });\n      else if (o.type in geometryType) geometryType[o.type](o.arcs, i);\n    }\n\n    var geometryType = {\n      LineString: line,\n      MultiLineString: polygon,\n      Polygon: polygon,\n      MultiPolygon: function(arcs, i) { arcs.forEach(function(arc) { polygon(arc, i); }); }\n    };\n\n    objects.forEach(geometry);\n\n    for (var i in indexesByArc) {\n      for (var indexes = indexesByArc[i], m = indexes.length, j = 0; j < m; ++j) {\n        for (var k = j + 1; k < m; ++k) {\n          var ij = indexes[j], ik = indexes[k], n;\n          if ((n = neighbors[ij])[i = bisect(n, ik)] !== ik) n.splice(i, 0, ik);\n          if ((n = neighbors[ik])[i = bisect(n, ij)] !== ij) n.splice(i, 0, ij);\n        }\n      }\n    }\n\n    return neighbors;\n  }\n\n  function compareArea(a, b) {\n    return a[1][2] - b[1][2];\n  }\n\n  function minAreaHeap() {\n    var heap = {},\n        array = [],\n        size = 0;\n\n    heap.push = function(object) {\n      up(array[object._ = size] = object, size++);\n      return size;\n    };\n\n    heap.pop = function() {\n      if (size <= 0) return;\n      var removed = array[0], object;\n      if (--size > 0) object = array[size], down(array[object._ = 0] = object, 0);\n      return removed;\n    };\n\n    heap.remove = function(removed) {\n      var i = removed._, object;\n      if (array[i] !== removed) return; // invalid request\n      if (i !== --size) object = array[size], (compareArea(object, removed) < 0 ? up : down)(array[object._ = i] = object, i);\n      return i;\n    };\n\n    function up(object, i) {\n      while (i > 0) {\n        var j = ((i + 1) >> 1) - 1,\n            parent = array[j];\n        if (compareArea(object, parent) >= 0) break;\n        array[parent._ = i] = parent;\n        array[object._ = i = j] = object;\n      }\n    }\n\n    function down(object, i) {\n      while (true) {\n        var r = (i + 1) << 1,\n            l = r - 1,\n            j = i,\n            child = array[j];\n        if (l < size && compareArea(array[l], child) < 0) child = array[j = l];\n        if (r < size && compareArea(array[r], child) < 0) child = array[j = r];\n        if (j === i) break;\n        array[child._ = i] = child;\n        array[object._ = i = j] = object;\n      }\n    }\n\n    return heap;\n  }\n\n  function presimplify(topology, triangleArea) {\n    var absolute = transformAbsolute(topology.transform),\n        relative = transformRelative(topology.transform),\n        heap = minAreaHeap();\n\n    if (!triangleArea) triangleArea = cartesianTriangleArea;\n\n    topology.arcs.forEach(function(arc) {\n      var triangles = [],\n          maxArea = 0,\n          triangle,\n          i,\n          n,\n          p;\n\n      // To store each point’s effective area, we create a new array rather than\n      // extending the passed-in point to workaround a Chrome/V8 bug (getting\n      // stuck in smi mode). For midpoints, the initial effective area of\n      // Infinity will be computed in the next step.\n      for (i = 0, n = arc.length; i < n; ++i) {\n        p = arc[i];\n        absolute(arc[i] = [p[0], p[1], Infinity], i);\n      }\n\n      for (i = 1, n = arc.length - 1; i < n; ++i) {\n        triangle = arc.slice(i - 1, i + 2);\n        triangle[1][2] = triangleArea(triangle);\n        triangles.push(triangle);\n        heap.push(triangle);\n      }\n\n      for (i = 0, n = triangles.length; i < n; ++i) {\n        triangle = triangles[i];\n        triangle.previous = triangles[i - 1];\n        triangle.next = triangles[i + 1];\n      }\n\n      while (triangle = heap.pop()) {\n        var previous = triangle.previous,\n            next = triangle.next;\n\n        // If the area of the current point is less than that of the previous point\n        // to be eliminated, use the latter's area instead. This ensures that the\n        // current point cannot be eliminated without eliminating previously-\n        // eliminated points.\n        if (triangle[1][2] < maxArea) triangle[1][2] = maxArea;\n        else maxArea = triangle[1][2];\n\n        if (previous) {\n          previous.next = next;\n          previous[2] = triangle[2];\n          update(previous);\n        }\n\n        if (next) {\n          next.previous = previous;\n          next[0] = triangle[0];\n          update(next);\n        }\n      }\n\n      arc.forEach(relative);\n    });\n\n    function update(triangle) {\n      heap.remove(triangle);\n      triangle[1][2] = triangleArea(triangle);\n      heap.push(triangle);\n    }\n\n    return topology;\n  }\n\n  var version = \"1.6.26\";\n\n  exports.version = version;\n  exports.mesh = mesh;\n  exports.meshArcs = meshArcs;\n  exports.merge = merge;\n  exports.mergeArcs = mergeArcs;\n  exports.feature = feature;\n  exports.neighbors = neighbors;\n  exports.presimplify = presimplify;\n\n}));\n\n\t\t\tvar slicers = {};\n\t\t\tvar options;\n\n\t\t\tonmessage = function (e) {\n\t\t\t\tif (e.data[0] === 'slice') {\n\t\t\t\t\t// Given a blob of GeoJSON and some topojson/geojson-vt options, do the slicing.\n\t\t\t\t\tvar geojson = e.data[1];\n\t\t\t\t\toptions     = e.data[2];\n\n\t\t\t\t\tif (geojson.type && geojson.type === 'Topology') {\n\t\t\t\t\t\tfor (var layerName in geojson.objects) {\n\t\t\t\t\t\t\tslicers[layerName] = self.geojsonvt(\n\t\t\t\t\t\t\t\tself.topojson.feature(geojson, geojson.objects[layerName])\n\t\t\t\t\t\t\t, options);\n\t\t\t\t\t\t}\n\t\t\t\t\t} else {\n\t\t\t\t\t\tslicers[options.vectorTileLayerName] = self.geojsonvt(geojson, options);\n\t\t\t\t\t}\n\n\t\t\t\t} else if (e.data[0] === 'get') {\n\t\t\t\t\t// Gets the vector tile for the given coordinates, sends it back as a message\n\t\t\t\t\tvar coords = e.data[1];\n\n\t\t\t\t\tvar tileLayers = {};\n\t\t\t\t\tfor (var layerName in slicers) {\n\t\t\t\t\t\tvar slicedTileLayer = slicers[layerName].getTile(coords.z, coords.x, coords.y);\n\n\t\t\t\t\t\tif (slicedTileLayer) {\n\t\t\t\t\t\t\tvar vectorTileLayer = {\n\t\t\t\t\t\t\t\tfeatures: [],\n\t\t\t\t\t\t\t\textent: options.extent,\n\t\t\t\t\t\t\t\tname: options.vectorTileLayerName,\n\t\t\t\t\t\t\t\tlength: slicedTileLayer.features.length\n\t\t\t\t\t\t\t}\n\n\t\t\t\t\t\t\tfor (var i in slicedTileLayer.features) {\n\t\t\t\t\t\t\t\tvar feat = {\n\t\t\t\t\t\t\t\t\tgeometry: slicedTileLayer.features[i].geometry,\n\t\t\t\t\t\t\t\t\tproperties: slicedTileLayer.features[i].tags,\n\t\t\t\t\t\t\t\t\ttype: slicedTileLayer.features[i].type\t// 1 = point, 2 = line, 3 = polygon\n\t\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\t\tvectorTileLayer.features.push(feat);\n\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\ttileLayers[layerName] = vectorTileLayer;\n\t\t\t\t\t\t}\n\t\t\t\t\t}\n\t\t\t\t\tpostMessage({ layers: tileLayers, coords: coords });\n\t\t\t\t}\n\t\t\t}\n\t\t";

		// Create a shallow copy of this.options, excluding things that might
		// be functions - we only care about topojson/geojsonvt options
		var options = {};
		for (var i in this.options) {
			if (i !== 'rendererFactory' &&
				i !== 'vectorTileLayerStyles' &&
				typeof (this$1.options[i] !== 'function')
			) {
				options[i] = this$1.options[i];
			}
		}

		this._worker = new Worker(window.URL.createObjectURL(new Blob([workerCode])));

		// Send initial data to worker.
		this._worker.postMessage(['slice', geojson, options]);

	},


	_getVectorTilePromise: function(coords) {

		var _this = this;

		var p = new Promise( function waitForWorker(res) {
			_this._worker.addEventListener('message', function recv(m) {
				if (m.data.coords &&
				    m.data.coords.x === coords.x &&
				    m.data.coords.y === coords.y &&
				    m.data.coords.z === coords.z ) {

					res(m.data);
					_this._worker.removeEventListener('message', recv);
				}
			});
		});

		this._worker.postMessage(['get', coords]);

		return p;
	},

});


L.vectorGrid.slicer = function (geojson, options) {
	return new L.VectorGrid.Slicer(geojson, options);
};



// Network & Protobuf powered!
// NOTE: Assumes the globals `VectorTile` and `Pbf` exist!!!
L.VectorGrid.Protobuf = L.VectorGrid.extend({

	options: {
		subdomains: 'abc',	// Like L.TileLayer
	},


	initialize: function(url, options) {
		// Inherits options from geojson-vt!
// 		this._slicer = geojsonvt(geojson, options);
		this._url = url;
		L.VectorGrid.prototype.initialize.call(this, options);
	},


	_getSubdomain: L.TileLayer.prototype._getSubdomain,


	_getVectorTilePromise: function(coords) {
		var tileUrl = L.Util.template(this._url, L.extend({
			s: this._getSubdomain(coords),
			x: coords.x,
			y: coords.y,
			z: coords.z
// 			z: this._getZoomForUrl()	/// TODO: Maybe replicate TileLayer's maxNativeZoom
		}, this.options));

		return fetch(tileUrl).then(function(response){

			if (!response.ok) {
				return {layers:[]};
			}

			return response.blob().then( function (blob) {
// 				console.log(blob);

				var reader = new FileReader();
				return new Promise(function(resolve){
					reader.addEventListener("loadend", function() {
						// reader.result contains the contents of blob as a typed array

						// blob.type === 'application/x-protobuf'
						var pbf = new Pbf( reader.result );
// 						console.log(pbf);
						return resolve(new vectorTile.VectorTile( pbf ));

					});
					reader.readAsArrayBuffer(blob);
				});
			});
		}).then(function(json){

// 			console.log('Vector tile:', json.layers);
// 			console.log('Vector tile water:', json.layers.water);	// Instance of VectorTileLayer

			// Normalize feature getters into actual instanced features
			for (var layerName in json.layers) {
				var feats = [];

				for (var i=0; i<json.layers[layerName].length; i++) {
					var feat = json.layers[layerName].feature(i);
					feat.geometry = feat.loadGeometry();
					feats.push(feat);
				}

				json.layers[layerName].features = feats;
			}

			return json;
		});
	}
});


L.vectorGrid.protobuf = function (url, options) {
	return new L.VectorGrid.Protobuf(url, options);
};




//# sourceMappingURL=/home/ivan/devel/Leaflet.VectorGrid/.gobble-build/09-concat/1/Leaflet.VectorGrid.bundled.js.map
