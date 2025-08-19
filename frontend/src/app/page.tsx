"use client";
import { useState } from "react";

interface Results {
  message: string;
  totalContacts: number;
  totalErrors: number;
  duplicatesSkipped: number;
  runtime: number;
}
export default function Home() {
  const [filename, setFilename] = useState("");
  const [file, setFile] = useState<File>();
  const [results, setResults] = useState<Results>();
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) {
      return;
    }
    const file = event.target.files[0];
    if (file) {
      setFilename(file.name);
      setFile(file);
    } else {
      setFilename("");
      setFile(undefined);
    }
  };

  const handleOnSubmit = async () => {
    // if (!file) {
    //   return;
    // }
    // try {
    //   const response = await fetch("http://localhost:8000/upload", {
    //     method: "POST",
    //     body: file,
    //     headers: {
    //       "Access-Control-Allow-Origin": "*",
    //     },
    //   });
    //   const data = await response.json();
    //   console.log(data);
    // } catch (error) {
    //   console.error(error);
    // }
    if (!file) {
      return;
    }
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      console.log(data);
      setResults(data);
    } catch (error) {
      console.error(error);
    }
  };
  return (
    <div className="font-sans flex flex-col items-center justify-items-center min-h-screen p-8 pb-20 gap-40 sm:p-20">
      {/* Upload csv file */}

      <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center gap-3 w-[30vw] h-[40vh]">
        <label
          htmlFor="file"
          className="cursor-pointer bg-blue-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-blue-700 transition"
        >
          Select CSV File
        </label>
        <input
          type="file"
          id="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileChange}
        />
        <p className="text-gray-500 text-sm overflow-ellipsis">
          {filename || "Only .csv files are supported"}
        </p>
        <button
          className="bg-green-600 px-6 py-2 rounded-md font-semibold text-white hover:bg-green-700 transition mb-4"
          onClick={handleOnSubmit}
        >
          Upload
        </button>
        <div className="w-full h-[1px] bg-gray-300" />
        <h1 className="text-3xl font-bold text-black">Summary</h1>
        {results && (
          <div className="flex flex-col gap-2 w-full">
            <ul>
              <li className="mb-2 tracking-[-.01em] text-xl text-black">
                <p>Total Contacts Imported: {results.totalContacts}</p>
              </li>
              <li className="mb-2 tracking-[-.01em] text-xl text-black">
                <p>Total Errors: {results.totalErrors}</p>
              </li>
              <li className="mb-2 tracking-[-.01em] text-xl text-black">
                <p>Duplicates Skipped: {results.duplicatesSkipped}</p>
              </li>
              <li className="mb-2 tracking-[-.01em] text-xl text-black">
                <p>Runtime: {results.runtime.toFixed(2)} seconds</p>
              </li>
            </ul>
          </div>
        )}
      </div>

      {/* <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={180}
          height={38}
          priority
        />
        <ol className="font-mono list-inside list-decimal text-sm/6 text-center sm:text-left">
          <li className="mb-2 tracking-[-.01em]">
            Get started by editing{" "}
            <code className="bg-black/[.05] dark:bg-white/[.06] font-mono font-semibold px-1 py-0.5 rounded">
              src/app/page.tsx
            </code>
            .
          </li>
          <li className="tracking-[-.01em]">
            Save and see your changes instantly.
          </li>
        </ol>

        <div className="flex gap-4 items-center flex-col sm:flex-row">
          <a
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
            href="https://vercel.com/new?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              className="dark:invert"
              src="/vercel.svg"
              alt="Vercel logomark"
              width={20}
              height={20}
            />
            Deploy now
          </a>
          <a
            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto md:w-[158px]"
            href="https://nextjs.org/docs?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            Read our docs
          </a>
        </div>
      </main> */}
      {/* <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Learn
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Window icon"
            width={16}
            height={16}
          />
          Examples
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          Go to nextjs.org →
        </a>
      </footer> */}
    </div>
  );
}
