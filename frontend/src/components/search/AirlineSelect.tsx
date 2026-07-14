import { useState } from "react";
import { Check, ChevronsUpDown } from "lucide-react";

import airlines from "@/data/airlines.json";

import { Button } from "@/components/ui/button";

import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface Airline {
  code: string;
  name: string;
  display: string;
}

interface AirlineSelectProps {
  value: string;
  onChange: (value: string) => void;
}

export default function AirlineSelect({
  value,
  onChange,
}: AirlineSelectProps) {
  const [open, setOpen] = useState(false);

  const selectedAirline = (
    airlines as Airline[]
  ).find(
    (airline) => airline.code === value
  );

  return (
    <Popover
      open={open}
      onOpenChange={setOpen}
    >
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="   h-14 w-full
                        justify-between
                        rounded-xl
                        border-[#2a3950]
                        bg-[#0c182a]
                        px-4
                        font-normal
                        text-white
                        hover:bg-[#101e33]
                        hover:text-white
                        data-[state=open]:border-[#6f63e8]
                        data-[state=open]:bg-[#101e33]
                        "
        >
          <span className="truncate">
            {selectedAirline
              ? selectedAirline.display
              : "Select airline"}
          </span>

          <ChevronsUpDown className="ml-2 size-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>

      <PopoverContent
        className="
            w-[var(--radix-popover-trigger-width)]
            border-[#2a3950]
            bg-[#0c182a]
            p-0
            text-white
        "
        align="start"
        >
        <Command>
          <CommandInput placeholder="Search airline..." />

          <CommandList>
            <CommandEmpty>
              No airline found.
            </CommandEmpty>

            <CommandGroup>
              {(airlines as Airline[]).map(
                (airline) => (
                  <CommandItem
                    key={airline.code}
                    value={`${airline.name} ${airline.code}`}
                    onSelect={() => {
                      onChange(airline.code);
                      setOpen(false);
                    }}
                  >
                    <Check
                      className={`mr-2 size-4 ${
                        value === airline.code
                          ? "opacity-100"
                          : "opacity-0"
                      }`}
                    />

                    <div>
                      <p className="font-medium">
                        {airline.name}
                      </p>

                      <p className="text-xs text-muted-foreground">
                        {airline.code}
                      </p>
                    </div>
                  </CommandItem>
                )
              )}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}