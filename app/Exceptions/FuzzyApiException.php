<?php

namespace App\Exceptions;

use RuntimeException;

/** Kesalahan dari API Python; pesannya aman ditampilkan ke pengguna. */
class FuzzyApiException extends RuntimeException
{
}
